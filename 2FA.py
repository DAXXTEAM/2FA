import os
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import re
from time import time
from typing import Dict, Tuple

# Configuration from Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError(
        "❌ Missing environment variables!\n"
        "Please set API_ID, API_HASH, and BOT_TOKEN.\n"
        "Example:\n"
        "  export API_ID='your-api-id'\n"
        "  export API_HASH='your-api-hash'\n"
        "  export BOT_TOKEN='your-bot-token'"
    )

API_ID = int(API_ID)

# Initialize Bot
app = Client("2FA_Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Constants
BUTTON_COOLDOWN = 5  # seconds (reduced for better UX)
TOTP_INTERVAL = 30   # standard TOTP interval

# Storage (Note: Data is lost on restart - consider using a database for persistence)
user_2fa_keys: Dict[int, str] = {}
button_locks: Dict[Tuple[int, str], float] = {}
awaiting_key: Dict[int, bool] = {}  # Track users waiting to input a key


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


def get_totp_time_remaining() -> int:
    """Get seconds remaining until current TOTP code expires."""
    return TOTP_INTERVAL - (int(time()) % TOTP_INTERVAL)


def format_time_bar(seconds_remaining: int) -> str:
    """Create a visual progress bar for time remaining."""
    total_blocks = 10
    filled = int((seconds_remaining / TOTP_INTERVAL) * total_blocks)
    empty = total_blocks - filled
    return "█" * filled + "░" * empty


# Keyboards
def get_start_keyboard():
    """Generate the start menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Enter 2FA Key", callback_data="enter_2fa")],
        [InlineKeyboardButton("📚 About Bot", callback_data="about_bot"),
         InlineKeyboardButton("❓ Help", callback_data="help")]
    ])


def get_totp_keyboard():
    """Generate the TOTP options keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Code", callback_data="get_totp")],
        [InlineKeyboardButton("🔑 New Key", callback_data="enter_2fa"),
         InlineKeyboardButton("🗑️ Delete Key", callback_data="delete_key")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])


def get_back_keyboard():
    """Generate a simple back button keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
    ])


def get_confirm_delete_keyboard():
    """Generate confirmation keyboard for key deletion."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Delete", callback_data="confirm_delete"),
         InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]
    ])


# Command Handlers
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command."""
    user_id = message.from_user.id
    awaiting_key.pop(user_id, None)  # Clear any pending key input state
    
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    if has_key:
        await message.reply_text(
            "👋 **Welcome back!**\n\n"
            "✅ You have a 2FA key stored.\n"
            "Use the buttons below to manage your TOTP codes.",
            reply_markup=get_totp_keyboard()
        )
    else:
        await message.reply_text(
            "✨ **Welcome to the 2FA Manager Bot!** ✨\n\n"
            "🔒 **Features:**\n"
            "• Generate TOTP codes instantly\n"
            "• See time remaining for each code\n"
            "• Anti-spam protection\n\n"
            "🌟 **Get Started:**\n"
            "1️⃣ Click **'Enter 2FA Key'** below\n"
            "2️⃣ Send your secret key when prompted\n"
            "3️⃣ Generate codes anytime!\n\n"
            "⚠️ _Keys are stored in memory only and will be lost on bot restart._",
            reply_markup=get_start_keyboard()
        )


@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command."""
    await message.reply_text(
        "📖 **Help Guide**\n\n"
        "**Commands:**\n"
        "• /start - Start the bot\n"
        "• /help - Show this help message\n"
        "• /totp - Generate your TOTP code\n\n"
        "**What is 2FA?**\n"
        "Two-Factor Authentication adds an extra layer of security. "
        "This bot generates time-based one-time passwords (TOTP) that change every 30 seconds.\n\n"
        "**How to use:**\n"
        "1. Get your 2FA secret key from the service you want to protect\n"
        "2. Enter the key in this bot\n"
        "3. Use the generated codes to log in\n\n"
        "**Key Format:**\n"
        "Your key should be a Base32 string (A-Z, 2-7), typically 16+ characters.\n"
        "Example: `JBSWY3DPEHPK3PXP`",
        reply_markup=get_back_keyboard()
    )


@app.on_message(filters.command("totp"))
async def totp_command(client: Client, message: Message):
    """Handle the /totp command to quickly get a code."""
    user_id = message.from_user.id
    
    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await message.reply_text(
            "❌ **No key found!**\n\n"
            "Please add your 2FA key first.",
            reply_markup=get_start_keyboard()
        )
        return
    
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        time_remaining = get_totp_time_remaining()
        time_bar = format_time_bar(time_remaining)
        
        await message.reply_text(
            f"🔐 **Your TOTP Code:**\n\n"
            f"```{code}```\n\n"
            f"⏱️ **Expires in:** {time_remaining}s\n"
            f"[{time_bar}]",
            reply_markup=get_totp_keyboard()
        )
    except Exception as e:
        await message.reply_text(
            "❌ **Error generating code.**\n"
            "Your key might be invalid. Please enter a new key.",
            reply_markup=get_start_keyboard()
        )


# Callback Handlers
@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu(client: Client, callback: CallbackQuery):
    """Return to main menu."""
    user_id = callback.from_user.id
    awaiting_key.pop(user_id, None)
    
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    if has_key:
        await callback.message.edit_text(
            "🏠 **Main Menu**\n\n"
            "✅ You have a 2FA key stored.\n"
            "Use the buttons below to manage your TOTP codes.",
            reply_markup=get_totp_keyboard()
        )
    else:
        await callback.message.edit_text(
            "🏠 **Main Menu**\n\n"
            "Click a button below to get started.",
            reply_markup=get_start_keyboard()
        )
    await callback.answer()


@app.on_callback_query(filters.regex("^enter_2fa$"))
async def ask_2fa_key(client: Client, callback: CallbackQuery):
    """Prompt user to enter their 2FA key."""
    user_id = callback.from_user.id
    
    if is_button_locked(user_id, "enter_2fa"):
        remaining = get_remaining_time(user_id, "enter_2fa")
        await callback.answer(f"⏳ Wait {remaining}s before retrying.", show_alert=True)
        return

    lock_button(user_id, "enter_2fa")
    awaiting_key[user_id] = True
    
    await callback.message.edit_text(
        "📝 **Enter Your 2FA Secret Key:**\n\n"
        "Send your secret key as a message.\n\n"
        "**Requirements:**\n"
        "• Base32 format (A-Z, 2-7)\n"
        "• At least 16 characters\n"
        "• No spaces or special characters\n\n"
        "**Example:** `JBSWY3DPEHPK3PXP`\n\n"
        "⚠️ _Your key is stored securely in memory._",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^get_totp$"))
async def generate_totp(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    user_id = callback.from_user.id
    
    if is_button_locked(user_id, "get_totp"):
        remaining = get_remaining_time(user_id, "get_totp")
        await callback.answer(f"⏳ Wait {remaining}s", show_alert=True)
        return

    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.message.edit_text(
            "❌ **No key found!**\n\n"
            "Please enter your 2FA key first.",
            reply_markup=get_start_keyboard()
        )
        await callback.answer()
        return

    lock_button(user_id, "get_totp")
    
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        time_remaining = get_totp_time_remaining()
        time_bar = format_time_bar(time_remaining)
        
        await callback.message.edit_text(
            f"🔐 **Your TOTP Code:**\n\n"
            f"```{code}```\n\n"
            f"⏱️ **Expires in:** {time_remaining}s\n"
            f"[{time_bar}]\n\n"
            f"💡 _Click 'Refresh' for a new code._",
            reply_markup=get_totp_keyboard()
        )
        await callback.answer("✅ Code generated!")
    except Exception:
        await callback.message.edit_text(
            "❌ **Error generating code.**\n\n"
            "Your stored key might be invalid.\n"
            "Please enter a new key.",
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
        "⚠️ **Delete 2FA Key?**\n\n"
        "Are you sure you want to delete your stored key?\n"
        "This action cannot be undone.",
        reply_markup=get_confirm_delete_keyboard()
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^confirm_delete$"))
async def confirm_delete_key(client: Client, callback: CallbackQuery):
    """Delete the user's 2FA key."""
    user_id = callback.from_user.id
    
    if user_id in user_2fa_keys:
        del user_2fa_keys[user_id]
    
    awaiting_key.pop(user_id, None)
    
    await callback.message.edit_text(
        "✅ **Key Deleted!**\n\n"
        "Your 2FA key has been removed.\n"
        "You can add a new key anytime.",
        reply_markup=get_start_keyboard()
    )
    await callback.answer("Key deleted!")


@app.on_callback_query(filters.regex("^about_bot$"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    await callback.message.edit_text(
        "🤖 **About 2FA Manager Bot**\n\n"
        "**Version:** 2.0\n\n"
        "🔐 **What it does:**\n"
        "• Stores your 2FA secret keys\n"
        "• Generates TOTP codes on demand\n"
        "• Shows time remaining for each code\n\n"
        "🛡️ **Security:**\n"
        "• Keys stored in memory only\n"
        "• No data persisted to disk\n"
        "• Anti-spam cooldown protection\n\n"
        "📚 **Built with:**\n"
        "• Python + Pyrogram\n"
        "• PyOTP for TOTP generation\n\n"
        "💻 **Source:** [GitHub](https://github.com/DAXXTEAM/2FA)",
        reply_markup=get_back_keyboard(),
        disable_web_page_preview=True
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback: CallbackQuery):
    """Show help via callback."""
    await callback.message.edit_text(
        "📖 **Help Guide**\n\n"
        "**Commands:**\n"
        "• /start - Start the bot\n"
        "• /help - Show this help\n"
        "• /totp - Quick code generation\n\n"
        "**What is TOTP?**\n"
        "Time-based One-Time Passwords change every 30 seconds "
        "and add extra security to your accounts.\n\n"
        "**How to use:**\n"
        "1. Get your 2FA secret key from the service\n"
        "2. Click 'Enter 2FA Key' and send the key\n"
        "3. Click 'Refresh Code' to generate codes\n\n"
        "**Key Format:**\n"
        "Base32 string (A-Z, 2-7), 16+ characters\n"
        "Example: `JBSWY3DPEHPK3PXP`",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


# Message Handler for 2FA Key Input
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "totp"]))
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    user_id = message.from_user.id
    
    # Only process if user is awaiting key input
    if user_id not in awaiting_key or not awaiting_key[user_id]:
        return
    
    key = message.text.strip().replace(" ", "").replace("-", "").upper()
    
    # Delete the message containing the key for security
    try:
        await message.delete()
    except Exception:
        pass  # May not have permission to delete
    
    if not is_valid_base32(key):
        await message.reply_text(
            "🚫 **Invalid Key Format!**\n\n"
            "**Requirements:**\n"
            "• Only A-Z and 2-7 characters\n"
            "• At least 16 characters long\n"
            "• No spaces or special characters\n\n"
            "Please try again or click 'Back' to cancel.",
            reply_markup=get_back_keyboard()
        )
        return

    try:
        # Verify the key works
        totp = pyotp.TOTP(key)
        code = totp.now()
        time_remaining = get_totp_time_remaining()
        time_bar = format_time_bar(time_remaining)
        
        # Save the key
        user_2fa_keys[user_id] = key
        awaiting_key.pop(user_id, None)
        
        await message.reply_text(
            f"✅ **2FA Key Saved Successfully!**\n\n"
            f"🔐 **Your First Code:**\n\n"
            f"```{code}```\n\n"
            f"⏱️ **Expires in:** {time_remaining}s\n"
            f"[{time_bar}]\n\n"
            f"💡 _Use the buttons below to manage your codes._",
            reply_markup=get_totp_keyboard()
        )
    except Exception as e:
        await message.reply_text(
            "❌ **Error Processing Key**\n\n"
            "The key appears invalid. Please check and try again.",
            reply_markup=get_back_keyboard()
        )


if __name__ == "__main__":
    print("=" * 50)
    print("🚀 2FA Manager Bot v2.0")
    print("=" * 50)
    print("✅ Bot is starting...")
    print("📝 Commands: /start, /help, /totp")
    print("=" * 50)
    app.run()
