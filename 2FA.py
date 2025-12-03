import os
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait, RPCError
import pyotp
import re
from time import time
from typing import Dict, Tuple, Optional
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from Environment Variables (NO DEFAULT VALUES FOR SECURITY)
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError(
        "❌ CRITICAL: API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.\n"
        "Please configure these environment variables before running the bot."
    )

try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("API_ID must be a valid integer")

# Initialize the client
app = Client(
    "adv_2fa_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Constants
BUTTON_COOLDOWN = 30  # seconds

# Storage (In-Memory - Data will be lost on restart)
# WARNING: For production use, consider implementing persistent storage (e.g., Redis, SQLite)
user_2fa_keys: Dict[int, Optional[str]] = {}
button_locks: Dict[Tuple[int, str], float] = {}

logger.warning(
    "⚠️  Using in-memory storage. All 2FA keys will be lost when the bot restarts. "
    "Consider implementing persistent storage for production use."
)

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
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    logger.info(f"User {user_id} (@{username}) started the bot")
    
    try:
        await message.reply_text(
            "✨ **Welcome to the Animated 2FA Manager!** ✨\n\n"
            "🔒 **Features:**\n"
            "• Securely store your 2FA keys (session-based)\n"
            "• Generate TOTP codes instantly\n"
            "• Anti-spam button cooldown\n\n"
            "🌟 **Get Started:**\n"
            "1️⃣ Click **'Enter 2FA Key'** below\n"
            "2️⃣ Send your 2FA key when prompted\n"
            "3️⃣ Use the **Generate TOTP Code** button anytime!\n\n"
            "⚠️ **Note:** Keys are stored in memory and will be cleared on bot restart.\n\n"
            "🎉 _Let's get started!_",
            reply_markup=get_start_keyboard()
        )
    except FloodWait as e:
        logger.warning(f"FloodWait for {e.value} seconds")
        await asyncio.sleep(e.value)
        await start_command(client, message)
    except Exception as e:
        logger.error(f"Error in start_command: {e}", exc_info=True)
        await message.reply_text("❌ An error occurred. Please try again later.")

@app.on_callback_query(filters.regex("enter_2fa"))
async def ask_2fa_key(client: Client, callback: CallbackQuery):
    """Prompt user to enter their 2FA key."""
    user_id = callback.from_user.id
    username = callback.from_user.username or "Unknown"
    
    try:
        if is_button_locked(user_id, "enter_2fa"):
            remaining = get_remaining_time(user_id, "enter_2fa")
            await callback.answer(f"⏳ Wait {remaining} seconds before retrying.", show_alert=True)
            logger.info(f"User {user_id} (@{username}) hit cooldown for enter_2fa")
            return

        lock_button(user_id, "enter_2fa")
        logger.info(f"User {user_id} (@{username}) requested to enter 2FA key")
        
        await callback.message.edit_text(
            "📝 **Enter Your 2FA Key:**\n\n"
            "➡️ The key must be a valid Base32 string.\n"
            "Example: `JBSWY3DPEHPK3PXP`\n\n"
            "🔒 _Your key is stored securely in this session._"
        )
        user_2fa_keys[user_id] = None
        await callback.answer()
    except FloodWait as e:
        logger.warning(f"FloodWait for {e.value} seconds")
        await asyncio.sleep(e.value)
        await ask_2fa_key(client, callback)
    except Exception as e:
        logger.error(f"Error in ask_2fa_key: {e}", exc_info=True)
        await callback.answer("❌ An error occurred. Please try again.", show_alert=True)

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    user_id = message.from_user.id
    username = message.from_user.username or "Unknown"
    
    try:
        if user_id not in user_2fa_keys:
            await message.reply_text(
                "❌ Please restart using /start to begin.",
                reply_markup=get_start_keyboard()
            )
            return

        # Delete the message containing the key for security
        try:
            await message.delete()
        except Exception as e:
            logger.warning(f"Could not delete message with 2FA key: {e}")

        key = message.text.strip().replace(" ", "").upper()
        
        # Validate key length
        if len(key) < 16:
            await client.send_message(
                user_id,
                "🚫 **Key Too Short!**\n\n"
                "2FA keys are typically at least 16 characters long.\n\n"
                "ℹ️ Try again or use /start to reset."
            )
            return

        if not is_valid_base32(key):
            await client.send_message(
                user_id,
                "🚫 **Invalid Key Format!**\n\n"
                "Make sure your key follows the Base32 format:\n"
                "• Only uppercase letters A-Z and numbers 2-7 are allowed\n"
                "• No special characters or spaces\n\n"
                "ℹ️ Try again or use /start to reset."
            )
            return

        # Validate that the key can generate a TOTP code
        try:
            totp = pyotp.TOTP(key)
            test_code = totp.now()
            if not test_code or len(test_code) != 6:
                raise ValueError("Invalid TOTP code generated")
            
            user_2fa_keys[user_id] = key
            logger.info(f"User {user_id} (@{username}) successfully saved 2FA key")
            
            await client.send_message(
                user_id,
                "✅ **2FA Key Saved Successfully!**\n\n"
                "🎉 You can now generate TOTP codes using the button below.\n"
                "🔒 Your key is securely stored for this session.",
                reply_markup=get_totp_keyboard()
            )
        except Exception as e:
            logger.error(f"Error validating 2FA key for user {user_id}: {e}")
            await client.send_message(
                user_id,
                "❌ **Invalid 2FA Key!**\n\n"
                "The key you provided could not generate a valid TOTP code.\n"
                "Please verify your key and try again."
            )
    except Exception as e:
        logger.error(f"Error in handle_2fa_key: {e}", exc_info=True)
        try:
            await message.reply_text("❌ An error occurred processing your key. Please try again.")
        except:
            pass

@app.on_callback_query(filters.regex("get_totp"))
async def generate_totp(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    user_id = callback.from_user.id
    username = callback.from_user.username or "Unknown"
    
    try:
        if is_button_locked(user_id, "get_totp"):
            remaining = get_remaining_time(user_id, "get_totp")
            await callback.answer(f"⏳ Wait {remaining} seconds.", show_alert=True)
            logger.info(f"User {user_id} (@{username}) hit cooldown for get_totp")
            return

        if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
            await callback.message.edit_text(
                "❌ **No Key Found!**\n\n"
                "Please enter your 2FA key first to generate codes.",
                reply_markup=get_start_keyboard()
            )
            await callback.answer()
            return

        lock_button(user_id, "get_totp")
        
        try:
            totp = pyotp.TOTP(user_2fa_keys[user_id])
            code = totp.now()
            
            # Calculate time remaining for this code
            import time
            current_time = time.time()
            time_remaining = 30 - int(current_time % 30)
            
            logger.info(f"User {user_id} (@{username}) generated TOTP code")
            
            await callback.message.edit_text(
                f"🔐 **Your Current TOTP Code:**\n\n"
                f"✨ `{code}` ✨\n\n"
                f"⏱️ Valid for: **{time_remaining} seconds**\n\n"
                "⚡ _Generate a new code anytime!_",
                reply_markup=get_totp_keyboard()
            )
            await callback.answer("✅ Code generated!", show_alert=False)
        except Exception as e:
            logger.error(f"Error generating TOTP for user {user_id}: {e}", exc_info=True)
            await callback.message.edit_text(
                "❌ **Error Generating TOTP Code**\n\n"
                "There was an issue with your saved key. Please enter a new key.",
                reply_markup=get_start_keyboard()
            )
            # Clear the invalid key
            if user_id in user_2fa_keys:
                del user_2fa_keys[user_id]
            await callback.answer()
    except FloodWait as e:
        logger.warning(f"FloodWait for {e.value} seconds")
        await asyncio.sleep(e.value)
        await generate_totp(client, callback)
    except Exception as e:
        logger.error(f"Error in generate_totp: {e}", exc_info=True)
        await callback.answer("❌ An error occurred. Please try again.", show_alert=True)

@app.on_callback_query(filters.regex("about_bot"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    try:
        await callback.message.edit_text(
            "🤖 **About This Bot**\n\n"
            "🔒 **Security Features:**\n"
            "• Session-based key storage\n"
            "• Anti-spam cooldown protection\n"
            "• Automatic message deletion for keys\n\n"
            "🎯 **Functions:**\n"
            "• Store 2FA keys securely\n"
            "• Generate TOTP codes instantly\n"
            "• Real-time code validity display\n\n"
            "⚡ **Technology:**\n"
            "• Built with Pyrogram\n"
            "• TOTP via PyOTP\n"
            "• Async/await architecture\n\n"
            "⚠️ **Privacy Note:**\n"
            "Keys are stored in memory only and cleared on bot restart.\n\n"
            "💡 _Stay secure with 2FA!_",
            reply_markup=get_start_keyboard()
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in about_bot: {e}", exc_info=True)
        await callback.answer("❌ An error occurred.", show_alert=True)

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command."""
    try:
        await message.reply_text(
            "📚 **2FA Bot Help**\n\n"
            "**Commands:**\n"
            "• `/start` - Start the bot and access main menu\n"
            "• `/help` - Show this help message\n\n"
            "**How to Use:**\n"
            "1️⃣ Use `/start` to begin\n"
            "2️⃣ Click 'Enter 2FA Key' button\n"
            "3️⃣ Send your Base32 2FA key\n"
            "4️⃣ Click 'Generate TOTP Code' to get codes\n\n"
            "**Key Format:**\n"
            "• Must be Base32 encoded\n"
            "• Contains only A-Z and 2-7\n"
            "• Usually 16-32 characters\n"
            "• Example: `JBSWY3DPEHPK3PXP`\n\n"
            "**Security:**\n"
            "• Keys stored in memory only\n"
            "• Your messages are auto-deleted\n"
            "• Session-based storage\n\n"
            "Need support? Contact the bot administrator.",
            reply_markup=get_start_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in help_command: {e}", exc_info=True)
        await message.reply_text("❌ An error occurred. Please try /start")


async def main():
    """Main function to run the bot."""
    logger.info("=" * 50)
    logger.info("🚀 Starting 2FA Bot...")
    logger.info(f"📱 Bot token: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
    logger.info(f"🔑 API ID: {API_ID}")
    logger.info("=" * 50)
    
    try:
        await app.start()
        me = await app.get_me()
        logger.info(f"✅ Bot started successfully!")
        logger.info(f"👤 Bot username: @{me.username}")
        logger.info(f"🆔 Bot ID: {me.id}")
        logger.info(f"📝 Bot name: {me.first_name}")
        logger.info("=" * 50)
        logger.info("🟢 Bot is now running and ready to accept requests...")
        
        # Keep the bot running
        await app.idle()
        
    except KeyboardInterrupt:
        logger.info("🛑 Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logger.error(f"❌ Critical error occurred: {e}", exc_info=True)
        raise
    finally:
        logger.info("🔄 Stopping bot...")
        await app.stop()
        logger.info("✅ Bot stopped gracefully")


if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot shutdown complete")
    except Exception as e:
        logger.critical(f"💥 Fatal error: {e}", exc_info=True)
        exit(1)
