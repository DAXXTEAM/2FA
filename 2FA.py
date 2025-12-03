import os
import logging
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import re
from time import time
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration from Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError(
        "❌ Missing required environment variables!\n"
        "Please set API_ID, API_HASH, and BOT_TOKEN before running the bot."
    )

API_ID = int(API_ID)

# Initialize Bot
app = Client(
    "2FA_Bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Configuration
BUTTON_COOLDOWN = 30  # seconds
TOTP_INTERVAL = 30  # TOTP code validity period

# Storage
user_2fa_keys: Dict[int, str] = {}
button_locks: Dict[Tuple[int, str], float] = {}
awaiting_key_input: Dict[int, bool] = {}


# Helper Functions
def is_valid_base32(s: str) -> bool:
    """Check if the string is valid Base32."""
    if not s:
        return False
    # Remove padding and check
    s_clean = s.rstrip("=")
    base32_pattern = r"^[A-Z2-7]+$"
    return bool(re.match(base32_pattern, s_clean)) and len(s_clean) >= 16


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


def get_totp_remaining_seconds() -> int:
    """Get remaining seconds until current TOTP code expires."""
    return TOTP_INTERVAL - (int(time()) % TOTP_INTERVAL)


def format_remaining_bar(remaining: int) -> str:
    """Create a visual progress bar for TOTP expiry."""
    total_blocks = 10
    filled_blocks = (remaining * total_blocks) // TOTP_INTERVAL
    empty_blocks = total_blocks - filled_blocks
    return "█" * filled_blocks + "░" * empty_blocks


# Keyboards
def get_start_keyboard() -> InlineKeyboardMarkup:
    """Generate the start menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Enter 2FA Key", callback_data="enter_2fa")],
        [InlineKeyboardButton("📚 About Bot", callback_data="about_bot"),
         InlineKeyboardButton("❓ Help", callback_data="help")]
    ])


def get_totp_keyboard() -> InlineKeyboardMarkup:
    """Generate the TOTP options keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Generate TOTP Code", callback_data="get_totp")],
        [InlineKeyboardButton("🔑 Enter New Key", callback_data="enter_2fa"),
         InlineKeyboardButton("🗑️ Delete Key", callback_data="delete_key")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Generate a back button keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ])


def get_confirm_delete_keyboard() -> InlineKeyboardMarkup:
    """Generate delete confirmation keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Delete", callback_data="confirm_delete"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")]
    ])


# Command Handlers
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command."""
    user = message.from_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot")
    
    welcome_text = (
        f"✨ **Welcome, {user.first_name}!** ✨\n\n"
        "🔒 **2FA Manager Bot**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "🎯 **Features:**\n"
        "• 🔐 Securely store your 2FA keys\n"
        "• ⚡ Generate TOTP codes instantly\n"
        "• ⏱️ See code expiry countdown\n"
        "• 🛡️ Anti-spam button cooldown\n\n"
        "🚀 **Get Started:**\n"
        "1️⃣ Click **'Enter 2FA Key'** below\n"
        "2️⃣ Send your 2FA secret key\n"
        "3️⃣ Generate codes anytime!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "🎉 _Let's secure your accounts!_"
    )
    
    await message.reply_text(welcome_text, reply_markup=get_start_keyboard())


@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command."""
    await show_help(message)


async def show_help(message_or_callback):
    """Show help information."""
    help_text = (
        "📖 **How to Use This Bot**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "**1️⃣ Getting Your 2FA Key:**\n"
        "• Open your authenticator app\n"
        "• Find the 'secret key' or 'setup key'\n"
        "• It looks like: `JBSWY3DPEHPK3PXP`\n\n"
        "**2️⃣ Adding Your Key:**\n"
        "• Click 'Enter 2FA Key'\n"
        "• Send your secret key\n"
        "• The key must be Base32 format\n\n"
        "**3️⃣ Generating Codes:**\n"
        "• Click 'Generate TOTP Code'\n"
        "• Tap the code to copy it\n"
        "• Codes refresh every 30 seconds\n\n"
        "**⚠️ Security Tips:**\n"
        "• Never share your 2FA key\n"
        "• Delete your key when done\n"
        "• Keys are stored in memory only\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 **Commands:** /start, /help"
    )
    
    if isinstance(message_or_callback, Message):
        await message_or_callback.reply_text(help_text, reply_markup=get_back_keyboard())
    else:
        await message_or_callback.message.edit_text(help_text, reply_markup=get_back_keyboard())


@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu(client: Client, callback: CallbackQuery):
    """Return to main menu."""
    user = callback.from_user
    awaiting_key_input.pop(user.id, None)
    
    welcome_text = (
        f"✨ **Welcome back, {user.first_name}!** ✨\n\n"
        "🔒 **2FA Manager Bot**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose an option below to get started."
    )
    
    await callback.message.edit_text(welcome_text, reply_markup=get_start_keyboard())
    await callback.answer()


@app.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback: CallbackQuery):
    """Handle help button click."""
    await show_help(callback)
    await callback.answer()


@app.on_callback_query(filters.regex("^enter_2fa$"))
async def ask_2fa_key(client: Client, callback: CallbackQuery):
    """Prompt user to enter their 2FA key."""
    user_id = callback.from_user.id
    
    if is_button_locked(user_id, "enter_2fa"):
        remaining = get_remaining_time(user_id, "enter_2fa")
        await callback.answer(f"⏳ Please wait {remaining}s before retrying.", show_alert=True)
        return

    lock_button(user_id, "enter_2fa")
    awaiting_key_input[user_id] = True
    
    prompt_text = (
        "📝 **Enter Your 2FA Secret Key**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "➡️ Send your Base32 secret key now.\n\n"
        "**Format:**\n"
        "• Only letters A-Z and digits 2-7\n"
        "• Minimum 16 characters\n"
        "• Example: `JBSWY3DPEHPK3PXP`\n\n"
        "🔒 _Your key is handled securely._\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "💡 _Tip: Copy-paste your key for accuracy_"
    )
    
    await callback.message.edit_text(prompt_text, reply_markup=get_back_keyboard())
    await callback.answer()


@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    user_id = message.from_user.id
    
    # Check if user is expected to input a key
    if not awaiting_key_input.get(user_id):
        await message.reply_text(
            "❌ **Unexpected Input**\n\n"
            "Please use /start to begin or click a button.",
            reply_markup=get_start_keyboard()
        )
        return

    key = message.text.strip().replace(" ", "").replace("-", "").upper()
    
    # Validate Base32 format
    if not is_valid_base32(key):
        await message.reply_text(
            "🚫 **Invalid Key Format!**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "Your key must be valid Base32:\n"
            "• ✅ Characters: A-Z, 2-7\n"
            "• ✅ Minimum: 16 characters\n"
            "• ❌ No special characters\n\n"
            "**Example:** `JBSWY3DPEHPK3PXP`\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🔄 _Try again or click back to menu._",
            reply_markup=get_back_keyboard()
        )
        return

    # Validate key by generating a test TOTP
    try:
        totp = pyotp.TOTP(key)
        totp.now()  # Test generation
        
        user_2fa_keys[user_id] = key
        awaiting_key_input.pop(user_id, None)
        
        logger.info(f"User {user_id} saved a new 2FA key")
        
        await message.reply_text(
            "✅ **2FA Key Saved Successfully!**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎉 Your key has been stored.\n\n"
            "You can now generate TOTP codes\n"
            "using the button below!\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ _Click 'Generate TOTP Code' to start_",
            reply_markup=get_totp_keyboard()
        )
        
    except Exception as e:
        logger.error(f"Error validating key for user {user_id}: {e}")
        await message.reply_text(
            "❌ **Invalid 2FA Key**\n\n"
            "The key you provided couldn't be validated.\n"
            "Please check and try again.",
            reply_markup=get_back_keyboard()
        )


@app.on_callback_query(filters.regex("^get_totp$"))
async def generate_totp(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    user_id = callback.from_user.id
    
    if is_button_locked(user_id, "get_totp"):
        remaining = get_remaining_time(user_id, "get_totp")
        await callback.answer(f"⏳ Please wait {remaining}s", show_alert=True)
        return

    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.message.edit_text(
            "❌ **No Key Found!**\n\n"
            "You haven't saved a 2FA key yet.\n"
            "Please enter your key first.",
            reply_markup=get_start_keyboard()
        )
        await callback.answer()
        return

    lock_button(user_id, "get_totp")
    
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        remaining_seconds = get_totp_remaining_seconds()
        progress_bar = format_remaining_bar(remaining_seconds)
        
        await callback.message.edit_text(
            "🔐 **Your TOTP Code**\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            f"```{code}```\n\n"
            f"⏱️ **Expires in:** {remaining_seconds}s\n"
            f"{progress_bar}\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 _Tap the code to copy it!_",
            reply_markup=get_totp_keyboard()
        )
        await callback.answer("✅ Code generated!")
        
    except Exception as e:
        logger.error(f"Error generating TOTP for user {user_id}: {e}")
        await callback.message.edit_text(
            "❌ **Error Generating Code**\n\n"
            "Something went wrong. Please try entering your key again.",
            reply_markup=get_start_keyboard()
        )
        await callback.answer("Error!", show_alert=True)


@app.on_callback_query(filters.regex("^delete_key$"))
async def delete_key_prompt(client: Client, callback: CallbackQuery):
    """Prompt user to confirm key deletion."""
    user_id = callback.from_user.id
    
    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.answer("No key to delete!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⚠️ **Delete 2FA Key?**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Are you sure you want to delete\n"
        "your saved 2FA key?\n\n"
        "**This action cannot be undone!**\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=get_confirm_delete_keyboard()
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^confirm_delete$"))
async def confirm_delete_key(client: Client, callback: CallbackQuery):
    """Delete the user's 2FA key."""
    user_id = callback.from_user.id
    
    if user_id in user_2fa_keys:
        del user_2fa_keys[user_id]
        logger.info(f"User {user_id} deleted their 2FA key")
    
    await callback.message.edit_text(
        "✅ **Key Deleted Successfully!**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "Your 2FA key has been removed.\n\n"
        "You can add a new key anytime\n"
        "using the menu below.\n\n"
        "━━━━━━━━━━━━━━━━━━━━",
        reply_markup=get_start_keyboard()
    )
    await callback.answer("Key deleted!")


@app.on_callback_query(filters.regex("^cancel_delete$"))
async def cancel_delete_key(client: Client, callback: CallbackQuery):
    """Cancel key deletion."""
    await callback.message.edit_text(
        "✅ **Deletion Cancelled**\n\n"
        "Your 2FA key is safe.",
        reply_markup=get_totp_keyboard()
    )
    await callback.answer("Cancelled")


@app.on_callback_query(filters.regex("^about_bot$"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    about_text = (
        "🤖 **About 2FA Manager Bot**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "**Version:** 2.0.0\n"
        "**Framework:** Pyrogram\n\n"
        "🔒 Securely manage your 2FA keys\n"
        "and generate TOTP codes with ease.\n\n"
        "**Features:**\n"
        "• ⚡ Instant code generation\n"
        "• ⏱️ Expiry countdown display\n"
        "• 🛡️ Anti-spam protection\n"
        "• 🗑️ Easy key management\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📌 **Open Source Project**\n"
        "🔗 [GitHub](https://github.com/DAXXTEAM/2FA)\n"
        "💬 [Support](https://t.me/vlubtech)"
    )
    
    await callback.message.edit_text(
        about_text,
        reply_markup=get_back_keyboard(),
        disable_web_page_preview=True
    )
    await callback.answer()


# Main entry point
if __name__ == "__main__":
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    logger.info("🚀 2FA Manager Bot Starting...")
    logger.info("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        app.run()
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
