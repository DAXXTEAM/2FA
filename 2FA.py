import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import re
from time import time
from typing import Dict, Tuple, Optional

# Configuration from Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError(
        "❌ Missing required environment variables!\n"
        "Please set: API_ID, API_HASH, and BOT_TOKEN"
    )

API_ID = int(API_ID)

# Bot Configuration
BUTTON_COOLDOWN = 5  # seconds (reduced for better UX)
TOTP_INTERVAL = 30  # standard TOTP interval

# Initialize the client
app = Client(
    "2fa_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Storage
user_2fa_keys: Dict[int, Optional[str]] = {}
user_key_names: Dict[int, str] = {}
button_locks: Dict[Tuple[int, str], float] = {}
awaiting_key_input: Dict[int, bool] = {}


# Helper Functions
def is_valid_base32(s: str) -> bool:
    """Check if the string is valid Base32."""
    # Remove spaces and convert to uppercase
    s = s.replace(" ", "").upper()
    # Base32 pattern - allows padding
    base32_pattern = r"^[A-Z2-7]+=*$"
    # Also check minimum length
    if len(s) < 16:
        return False
    return re.match(base32_pattern, s) is not None


def normalize_key(key: str) -> str:
    """Normalize a 2FA key by removing spaces and converting to uppercase."""
    return key.strip().replace(" ", "").upper()


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
    """Get remaining seconds until current TOTP expires."""
    return TOTP_INTERVAL - (int(time()) % TOTP_INTERVAL)


def format_totp_code(code: str) -> str:
    """Format TOTP code with space in middle for readability."""
    if len(code) == 6:
        return f"{code[:3]} {code[3:]}"
    return code


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
    """Generate a back to menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Back to Menu", callback_data="main_menu")]
    ])


def get_confirm_delete_keyboard():
    """Generate confirmation keyboard for key deletion."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Delete", callback_data="confirm_delete"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")]
    ])


# Command Handlers
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command."""
    user_id = message.from_user.id
    awaiting_key_input[user_id] = False
    
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    welcome_text = (
        "✨ **Welcome to 2FA Manager Bot!** ✨\n\n"
        "🔒 **Secure TOTP Code Generator**\n\n"
        "📌 **Features:**\n"
        "• Store your 2FA secret key securely\n"
        "• Generate TOTP codes instantly\n"
        "• Auto-refresh with countdown timer\n"
        "• Anti-spam protection\n\n"
    )
    
    if has_key:
        welcome_text += "✅ You have a key saved! Use the buttons below."
        await message.reply_text(welcome_text, reply_markup=get_totp_keyboard())
    else:
        welcome_text += "🚀 **Get Started:** Click the button below to add your 2FA key!"
        await message.reply_text(welcome_text, reply_markup=get_start_keyboard())


@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command."""
    await show_help(message)


async def show_help(message_or_callback):
    """Display help information."""
    help_text = (
        "📖 **How to Use This Bot**\n\n"
        "**Step 1:** Get your 2FA secret key\n"
        "• Open your authenticator app settings\n"
        "• Find the 'secret key' or 'setup key'\n"
        "• It looks like: `JBSWY3DPEHPK3PXP`\n\n"
        "**Step 2:** Save your key\n"
        "• Click '🔐 Enter 2FA Key'\n"
        "• Send your secret key to the bot\n\n"
        "**Step 3:** Generate codes\n"
        "• Click '🔄 Refresh Code' anytime\n"
        "• Codes refresh every 30 seconds\n\n"
        "**Commands:**\n"
        "• `/start` - Start the bot\n"
        "• `/help` - Show this help\n"
        "• `/totp` - Quick generate code\n"
        "• `/delete` - Delete saved key\n\n"
        "⚠️ **Security Note:**\n"
        "Keep your secret key private!"
    )
    
    if isinstance(message_or_callback, CallbackQuery):
        await message_or_callback.message.edit_text(
            help_text,
            reply_markup=get_back_keyboard()
        )
    else:
        await message_or_callback.reply_text(
            help_text,
            reply_markup=get_back_keyboard()
        )


@app.on_message(filters.command("totp"))
async def quick_totp_command(client: Client, message: Message):
    """Quick command to generate TOTP code."""
    user_id = message.from_user.id
    
    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await message.reply_text(
            "❌ **No key found!**\n\nPlease add your 2FA key first.",
            reply_markup=get_start_keyboard()
        )
        return
    
    await generate_and_send_totp(message, user_id)


@app.on_message(filters.command("delete"))
async def delete_command(client: Client, message: Message):
    """Command to delete saved key."""
    user_id = message.from_user.id
    
    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await message.reply_text(
            "ℹ️ **No key to delete!**\n\nYou haven't saved any 2FA key yet.",
            reply_markup=get_start_keyboard()
        )
        return
    
    await message.reply_text(
        "⚠️ **Delete Confirmation**\n\n"
        "Are you sure you want to delete your saved 2FA key?\n\n"
        "This action cannot be undone!",
        reply_markup=get_confirm_delete_keyboard()
    )


# Callback Handlers
@app.on_callback_query(filters.regex("^main_menu$"))
async def main_menu_callback(client: Client, callback: CallbackQuery):
    """Return to main menu."""
    user_id = callback.from_user.id
    awaiting_key_input[user_id] = False
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    menu_text = (
        "🏠 **Main Menu**\n\n"
        "Select an option below:"
    )
    
    if has_key:
        await callback.message.edit_text(menu_text, reply_markup=get_totp_keyboard())
    else:
        await callback.message.edit_text(menu_text, reply_markup=get_start_keyboard())
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
    awaiting_key_input[user_id] = True
    
    await callback.message.edit_text(
        "🔐 **Enter Your 2FA Secret Key**\n\n"
        "📝 Send your Base32 secret key now.\n\n"
        "**Format:** `JBSWY3DPEHPK3PXP`\n\n"
        "💡 **Where to find it:**\n"
        "• Authenticator app → Account settings\n"
        "• Look for 'Secret key' or 'Setup key'\n\n"
        "🔒 _Your key will be stored securely._",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^get_totp$"))
async def generate_totp_callback(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    user_id = callback.from_user.id
    
    if is_button_locked(user_id, "get_totp"):
        remaining = get_remaining_time(user_id, "get_totp")
        await callback.answer(f"⏳ Wait {remaining}s", show_alert=True)
        return

    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.message.edit_text(
            "❌ **No key found!**\n\nPlease enter your 2FA key first.",
            reply_markup=get_start_keyboard()
        )
        await callback.answer()
        return

    lock_button(user_id, "get_totp")
    
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        remaining_secs = get_totp_remaining_seconds()
        
        # Create visual timer bar
        filled = int((remaining_secs / 30) * 10)
        timer_bar = "█" * filled + "░" * (10 - filled)
        
        await callback.message.edit_text(
            f"🔐 **Your TOTP Code**\n\n"
            f"```\n{format_totp_code(code)}\n```\n\n"
            f"⏱️ **Expires in:** `{remaining_secs}s`\n"
            f"[{timer_bar}]\n\n"
            f"💡 _Tap the code to copy it!_",
            reply_markup=get_totp_keyboard()
        )
        await callback.answer("✅ Code generated!")
    except Exception as e:
        await callback.message.edit_text(
            "❌ **Error generating code!**\n\n"
            "Your saved key might be invalid.\n"
            "Please try entering a new key.",
            reply_markup=get_start_keyboard()
        )
        await callback.answer("Error!", show_alert=True)


@app.on_callback_query(filters.regex("^delete_key$"))
async def delete_key_callback(client: Client, callback: CallbackQuery):
    """Ask for confirmation to delete key."""
    user_id = callback.from_user.id
    
    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.answer("No key to delete!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⚠️ **Delete Confirmation**\n\n"
        "Are you sure you want to delete your saved 2FA key?\n\n"
        "**This action cannot be undone!**",
        reply_markup=get_confirm_delete_keyboard()
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^confirm_delete$"))
async def confirm_delete_callback(client: Client, callback: CallbackQuery):
    """Confirm key deletion."""
    user_id = callback.from_user.id
    
    if user_id in user_2fa_keys:
        del user_2fa_keys[user_id]
    if user_id in user_key_names:
        del user_key_names[user_id]
    
    await callback.message.edit_text(
        "✅ **Key Deleted Successfully!**\n\n"
        "Your 2FA key has been removed.\n"
        "You can add a new key anytime.",
        reply_markup=get_start_keyboard()
    )
    await callback.answer("Key deleted!", show_alert=True)


@app.on_callback_query(filters.regex("^cancel_delete$"))
async def cancel_delete_callback(client: Client, callback: CallbackQuery):
    """Cancel key deletion."""
    await callback.message.edit_text(
        "✅ **Deletion Cancelled**\n\n"
        "Your 2FA key is safe!",
        reply_markup=get_totp_keyboard()
    )
    await callback.answer("Cancelled!")


@app.on_callback_query(filters.regex("^about_bot$"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    await callback.message.edit_text(
        "🤖 **About 2FA Manager Bot**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔐 **What is 2FA?**\n"
        "Two-Factor Authentication adds an extra\n"
        "layer of security to your accounts.\n\n"
        "⚙️ **How it works:**\n"
        "• TOTP (Time-based One-Time Password)\n"
        "• Codes change every 30 seconds\n"
        "• Based on RFC 6238 standard\n\n"
        "🛡️ **Security:**\n"
        "• Keys stored in memory only\n"
        "• No data persistence between restarts\n"
        "• Open source & transparent\n\n"
        "📦 **Built with:**\n"
        "• Python + Pyrogram\n"
        "• PyOTP library\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=get_back_keyboard()
    )
    await callback.answer()


@app.on_callback_query(filters.regex("^help$"))
async def help_callback(client: Client, callback: CallbackQuery):
    """Show help information."""
    await show_help(callback)
    await callback.answer()


# Message Handler for 2FA Key Input
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "totp", "delete"]))
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    user_id = message.from_user.id
    
    # Check if user is in key input mode
    if not awaiting_key_input.get(user_id, False):
        await message.reply_text(
            "👋 **Hi there!**\n\n"
            "Use /start to begin or click a button from the menu.",
            reply_markup=get_start_keyboard()
        )
        return
    
    key = normalize_key(message.text)
    
    # Validate the key
    if not is_valid_base32(key):
        await message.reply_text(
            "🚫 **Invalid Key Format!**\n\n"
            "Your key must be:\n"
            "• At least 16 characters\n"
            "• Only letters A-Z and digits 2-7\n"
            "• No special characters\n\n"
            "**Example:** `JBSWY3DPEHPK3PXP`\n\n"
            "Please try again or use /start to cancel.",
            reply_markup=get_back_keyboard()
        )
        return

    # Try to generate a code to validate the key works
    try:
        totp = pyotp.TOTP(key)
        code = totp.now()
        
        # Save the key
        user_2fa_keys[user_id] = key
        awaiting_key_input[user_id] = False
        
        remaining_secs = get_totp_remaining_seconds()
        filled = int((remaining_secs / 30) * 10)
        timer_bar = "█" * filled + "░" * (10 - filled)
        
        await message.reply_text(
            f"✅ **2FA Key Saved Successfully!**\n\n"
            f"🔐 **Your Current Code:**\n"
            f"```\n{format_totp_code(code)}\n```\n\n"
            f"⏱️ **Expires in:** `{remaining_secs}s`\n"
            f"[{timer_bar}]\n\n"
            f"🎉 Use the buttons below to manage your codes!",
            reply_markup=get_totp_keyboard()
        )
    except Exception as e:
        await message.reply_text(
            "❌ **Error Processing Key!**\n\n"
            "The key appears invalid. Please check:\n"
            "• Is it the correct secret key?\n"
            "• Is it properly formatted?\n\n"
            "Try again or use /start to cancel.",
            reply_markup=get_back_keyboard()
        )


async def generate_and_send_totp(message: Message, user_id: int):
    """Generate and send TOTP code via message."""
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        remaining_secs = get_totp_remaining_seconds()
        
        filled = int((remaining_secs / 30) * 10)
        timer_bar = "█" * filled + "░" * (10 - filled)
        
        await message.reply_text(
            f"🔐 **Your TOTP Code**\n\n"
            f"```\n{format_totp_code(code)}\n```\n\n"
            f"⏱️ **Expires in:** `{remaining_secs}s`\n"
            f"[{timer_bar}]",
            reply_markup=get_totp_keyboard()
        )
    except Exception:
        await message.reply_text(
            "❌ Error generating code. Please try adding your key again.",
            reply_markup=get_start_keyboard()
        )


# Main Entry Point
if __name__ == "__main__":
    print("=" * 50)
    print("🚀 2FA Manager Bot Starting...")
    print("=" * 50)
    print("✅ Environment variables loaded")
    print("✅ Bot client initialized")
    print("📡 Connecting to Telegram...")
    print("=" * 50)
    app.run()
