import os
import logging
import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError
import pyotp
import re
from time import time
from typing import Dict, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from Environment Variables
try:
    API_ID = int(os.getenv("API_ID", "0"))
    API_HASH = os.getenv("API_HASH", "")
    BOT_TOKEN = os.getenv("BOT_TOKEN", "")
except ValueError:
    logger.error("API_ID must be a valid integer")
    raise

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]) or API_ID == 0:
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.")

# Initialize the client
app = Client(
    "2fa_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

BUTTON_COOLDOWN = 30  # seconds

# Storage
user_2fa_keys = {}
button_locks: Dict[Tuple[int, str], float] = {}

# Helper Functions
def is_valid_base32(s: str) -> bool:
    """Check if the string is valid Base32."""
    base32_pattern = r"^[A-Z2-7]+=*$"
    return re.match(base32_pattern, s) is not None

def is_button_locked(user_id: int, button_type: str) -> bool:
    """Check if a button is on cooldown."""
    key = (user_id, button_type)
    if key not in button_locks:
        return False
    if time() - button_locks[key] >= BUTTON_COOLDOWN:
        del button_locks[key]
        return False
    return True

def lock_button(user_id: int, button_type: str):
    """Lock a button for a cooldown period."""
    button_locks[(user_id, button_type)] = time()

def get_remaining_time(user_id: int, button_type: str) -> int:
    """Get remaining cooldown time for a button."""
    key = (user_id, button_type)
    if key not in button_locks:
        return 0
    remaining = int(BUTTON_COOLDOWN - (time() - button_locks[key]))
    return max(0, remaining)

# Keyboards
def get_start_keyboard():
    """Generate the start menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Enter 2FA Key", callback_data="enter_2fa")],
        [InlineKeyboardButton("📚 About Bot", callback_data="about_bot")]
    ])

def get_totp_keyboard():
    """Generate the TOTP options keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Generate TOTP Code", callback_data="get_totp")],
        [InlineKeyboardButton("🔑 Enter New Key", callback_data="enter_2fa")]
    ])

# Command Handlers
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command."""
    try:
        user = message.from_user
        logger.info(f"User {user.id} ({user.first_name}) started the bot")
        
        await message.reply_text(
            "✨ **Welcome to the Advanced 2FA Manager!** ✨\n\n"
            "🔒 **Features:**\n"
            "• Securely store your 2FA keys\n"
            "• Generate TOTP codes instantly\n"
            "• Anti-spam button cooldown\n"
            "• Privacy-focused (keys stored in memory)\n\n"
            "🌟 **Get Started:**\n"
            "1️⃣ Click **'Enter 2FA Key'** below\n"
            "2️⃣ Send your 2FA key when prompted\n"
            "3️⃣ Use the **Generate TOTP Code** button anytime!\n\n"
            "🎉 _Let's get started!_",
            reply_markup=get_start_keyboard()
        )
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds")
        await asyncio.sleep(e.value)
    except Exception as e:
        logger.error(f"Error in start_command: {e}", exc_info=True)
        await message.reply_text("❌ An error occurred. Please try again.")

@app.on_callback_query(filters.regex("enter_2fa"))
async def ask_2fa_key(client: Client, callback: CallbackQuery):
    """Prompt user to enter their 2FA key."""
    try:
        user_id = callback.from_user.id
        if is_button_locked(user_id, "enter_2fa"):
            remaining = get_remaining_time(user_id, "enter_2fa")
            await callback.answer(f"⏳ Wait {remaining} seconds before retrying.", show_alert=True)
            return

        lock_button(user_id, "enter_2fa")
        await callback.message.edit_text(
            "📝 **Enter Your 2FA Key:**\n\n"
            "➡️ The key must be a valid Base32 string.\n"
            "Example: `JBSWY3DPEHPK3PXP`\n\n"
            "🔒 _Your key is stored securely in memory only._\n\n"
            "💡 **Tip:** Get your key from your authenticator app's settings."
        )
        user_2fa_keys[user_id] = None
        logger.info(f"User {user_id} requested to enter 2FA key")
    except Exception as e:
        logger.error(f"Error in ask_2fa_key: {e}", exc_info=True)
        await callback.answer("❌ An error occurred. Please try /start again.", show_alert=True)

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "remove"]))
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    try:
        user_id = message.from_user.id
        if user_id not in user_2fa_keys:
            await message.reply_text(
                "❌ Please start by using /start first.",
                reply_markup=get_start_keyboard()
            )
            return

        key = message.text.strip().replace(" ", "").replace("-", "").upper()

        # Check key length (typical 2FA keys are 16-32 characters)
        if len(key) < 16:
            await message.reply_text(
                "🚫 **Key too short!**\n\n"
                "2FA keys are typically at least 16 characters long.\n\n"
                "ℹ️ Try again or use /start to reset."
            )
            return

        if not is_valid_base32(key):
            await message.reply_text(
                "🚫 **Invalid Key Format!**\n\n"
                "Make sure your key follows the Base32 format:\n"
                "• Only A-Z and 2-7 are allowed\n"
                "• No special characters (spaces/hyphens will be removed)\n\n"
                "ℹ️ Try again or use /start to reset."
            )
            return

        # Validate the key by generating a code
        pyotp.TOTP(key).now()
        user_2fa_keys[user_id] = key
        logger.info(f"User {user_id} successfully saved 2FA key")
        
        await message.reply_text(
            "✅ **2FA Key Saved Successfully!**\n\n"
            "🎉 You can now generate TOTP codes using the button below.\n\n"
            "🔐 Your key is stored securely in memory only.",
            reply_markup=get_totp_keyboard()
        )
    except ValueError as e:
        logger.warning(f"Invalid 2FA key from user {user_id}: {e}")
        await message.reply_text(
            "❌ **Invalid 2FA Key!**\n\n"
            "The key you provided couldn't generate a valid TOTP code.\n\n"
            "Please double-check your key and try again."
        )
    except Exception as e:
        logger.error(f"Error in handle_2fa_key: {e}", exc_info=True)
        await message.reply_text("❌ An unexpected error occurred. Please try again.")

@app.on_callback_query(filters.regex("get_totp"))
async def generate_totp(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    try:
        user_id = callback.from_user.id
        if is_button_locked(user_id, "get_totp"):
            remaining = get_remaining_time(user_id, "get_totp")
            await callback.answer(f"⏳ Wait {remaining} seconds.", show_alert=True)
            return

        if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
            await callback.message.edit_text(
                "❌ No key found! Please enter your key first.",
                reply_markup=get_start_keyboard()
            )
            return

        lock_button(user_id, "get_totp")
        
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        
        # Calculate time remaining for this code
        remaining_time = 30 - (int(time()) % 30)
        
        logger.info(f"Generated TOTP code for user {user_id}")
        
        await callback.message.edit_text(
            f"🔐 **Your Current TOTP Code:**\n\n"
            f"✨ `{code}` ✨\n\n"
            f"⏱ Valid for: **{remaining_time}** seconds\n\n"
            "⚡ _Generate a new code anytime!_",
            reply_markup=get_totp_keyboard()
        )
        await callback.answer("✅ TOTP code generated!", show_alert=False)
    except Exception as e:
        logger.error(f"Error in generate_totp: {e}", exc_info=True)
        await callback.message.edit_text(
            "❌ Error generating your TOTP code.\n\n"
            "Please try entering your key again.",
            reply_markup=get_start_keyboard()
        )

@app.on_callback_query(filters.regex("about_bot"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    try:
        await callback.message.edit_text(
            "🤖 **About This Bot**:\n\n"
            "🔒 Securely manage your 2FA keys and generate TOTP codes\n"
            "🎨 Modern interface with anti-spam protection\n"
            "🔐 Privacy-focused: Keys stored in memory only\n"
            "⚡ Instant TOTP code generation\n\n"
            "**Commands:**\n"
            "• /start - Start the bot\n"
            "• /help - Get help\n"
            "• /remove - Remove your stored key\n\n"
            "💡 _Built with Pyrogram & PyOTP_\n"
            "🛡️ _Open source & secure_",
            reply_markup=get_start_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in about_bot: {e}", exc_info=True)
        await callback.answer("❌ An error occurred.", show_alert=True)

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command."""
    try:
        await message.reply_text(
            "📚 **Help & Instructions**\n\n"
            "**How to use:**\n"
            "1️⃣ Use /start to begin\n"
            "2️⃣ Click 'Enter 2FA Key' button\n"
            "3️⃣ Send your 2FA secret key (Base32 format)\n"
            "4️⃣ Click 'Generate TOTP Code' to get your code\n\n"
            "**Where to find your 2FA key?**\n"
            "• Most authenticator apps have an 'Export' or 'Show key' option\n"
            "• It's usually a 16-32 character string\n"
            "• Example: JBSWY3DPEHPK3PXP\n\n"
            "**Commands:**\n"
            "• /start - Start the bot\n"
            "• /help - Show this help message\n"
            "• /remove - Remove your stored key\n\n"
            "**Security:**\n"
            "• Keys are stored in memory only\n"
            "• Keys are NOT saved to disk\n"
            "• Restart will clear all keys\n\n"
            "🔒 _Your security is our priority!_",
            reply_markup=get_start_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in help_command: {e}", exc_info=True)

@app.on_message(filters.command("remove"))
async def remove_key_command(client: Client, message: Message):
    """Handle the /remove command to delete stored key."""
    try:
        user_id = message.from_user.id
        if user_id in user_2fa_keys:
            del user_2fa_keys[user_id]
            logger.info(f"User {user_id} removed their 2FA key")
            await message.reply_text(
                "✅ **Key Removed Successfully!**\n\n"
                "Your 2FA key has been deleted from memory.\n\n"
                "Use /start to add a new key.",
                reply_markup=get_start_keyboard()
            )
        else:
            await message.reply_text(
                "ℹ️ **No Key Found**\n\n"
                "You don't have any stored key.\n\n"
                "Use /start to add one.",
                reply_markup=get_start_keyboard()
            )
    except Exception as e:
        logger.error(f"Error in remove_key_command: {e}", exc_info=True)
        await message.reply_text("❌ An error occurred.")

if __name__ == "__main__":
    logger.info("🚀 Starting 2FA Bot...")
    print("🚀 2FA Bot is now running...")
    try:
        app.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
    finally:
        logger.info("Bot shutting down...")
    
