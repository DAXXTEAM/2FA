import os
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import re
from time import time
from typing import Dict, Tuple

# Configuration from Environment Variables
API_ID = int(os.getenv("API_ID", "24509589"))
API_HASH = os.getenv("API_HASH", "717cf21d94c4934bcbe1eaa1ad86ae75")
BOT_TOKEN = os.getenv("BOT_TOKEN", "8148561075:AAHWEUHbbcWCyTtwLFYGEY5FMr8wxE4b5c4")

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.")

# Initialize Bot
bot = Client("2FA_Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
BUTTON_COOLDOWN = 30  # seconds

# Initialize the client
app = Client("adv_2fa_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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
    await message.reply_text(
        "✨ **Welcome to the Animated 2FA Manager!** ✨\n\n"
        "🔒 **Features:**\n"
        "• Securely store your 2FA keys\n"
        "• Generate TOTP codes instantly\n"
        "• Anti-spam button cooldown\n\n"
        "🌟 **Get Started:**\n"
        "1️⃣ Click **'Enter 2FA Key'** below\n"
        "2️⃣ Send your 2FA key when prompted\n"
        "3️⃣ Use the **Generate TOTP Code** button anytime!\n\n"
        "🎉 _Let's get started!_",
        reply_markup=get_start_keyboard()
    )

@app.on_callback_query(filters.regex("enter_2fa"))
async def ask_2fa_key(client: Client, callback: CallbackQuery):
    """Prompt user to enter their 2FA key."""
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
        "🔒 _Your key is stored securely._"
    )
    user_2fa_keys[user_id] = None

@app.on_message(filters.private & filters.text)
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    user_id = message.from_user.id
    if user_id not in user_2fa_keys:
        await message.reply_text("❌ Please restart using /start.", reply_markup=get_start_keyboard())
        return

    key = message.text.strip().replace(" ", "").upper()

    if not is_valid_base32(key):
        await message.reply_text(
            "🚫 **Invalid Key!**\n\n"
            "Make sure your key follows the Base32 format:\n"
            "• Only A-Z, 2-7 are allowed\n"
            "• No special characters or spaces\n\n"
            "ℹ️ Try again or use /start to reset."
        )
        return

    try:
        pyotp.TOTP(key).now()
        user_2fa_keys[user_id] = key
        await message.reply_text(
            "✅ **2FA Key Saved!**\n\n"
            "🎉 You can now generate TOTP codes using the button below.",
            reply_markup=get_totp_keyboard()
        )
    except Exception:
        await message.reply_text("❌ Error saving your key. Please try again.")

@app.on_callback_query(filters.regex("get_totp"))
async def generate_totp(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    user_id = callback.from_user.id
    if is_button_locked(user_id, "get_totp"):
        remaining = get_remaining_time(user_id, "get_totp")
        await callback.answer(f"⏳ Wait {remaining} seconds.", show_alert=True)
        return

    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.message.edit_text("❌ No key found! Please enter your key first.", reply_markup=get_start_keyboard())
        return

    lock_button(user_id, "get_totp")
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        await callback.message.edit_text(
            f"🔐 **Your Current TOTP Code:**\n\n"
            f"✨ `{code}` ✨\n\n"
            "⚡ _Generate a new code anytime!_",
            reply_markup=get_totp_keyboard()
        )
    except Exception:
        await callback.message.edit_text("❌ Error generating your TOTP code.")

@app.on_callback_query(filters.regex("about_bot"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    await callback.message.edit_text(
        "🤖 **About This Bot**:\n\n"
        "🔒 Manage your 2FA keys and generate secure TOTP codes with ease.\n"
        "🎨 Designed with animations and enhanced features for a seamless experience.\n\n"
        "💡 _Built using Pyrogram._",
        reply_markup=get_start_keyboard()
    )

if __name__ == "__main__":
    print("🚀  2FA Bot is now running...")
    app.run()
    
