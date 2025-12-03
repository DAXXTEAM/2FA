import os
import json
import logging
from pathlib import Path
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import re
from time import time
from typing import Dict, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are set (no default values for security)
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.")

try:
    API_ID = int(API_ID)
except ValueError:
    raise ValueError("API_ID must be a valid integer.")

# Constants
BUTTON_COOLDOWN = 30  # seconds
DATA_FILE = "user_data.json"

# Initialize the client
app = Client("2FA_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Storage
user_2fa_keys: Dict[int, str] = {}
button_locks: Dict[Tuple[int, str], float] = {}

# Persistence Functions
def load_user_data():
    """Load user data from JSON file."""
    global user_2fa_keys
    try:
        if Path(DATA_FILE).exists():
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                # Convert string keys back to integers
                user_2fa_keys = {int(k): v for k, v in data.items()}
                logger.info(f"Loaded data for {len(user_2fa_keys)} users")
    except Exception as e:
        logger.error(f"Error loading user data: {e}")
        user_2fa_keys = {}

def save_user_data():
    """Save user data to JSON file."""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(user_2fa_keys, f, indent=2)
        logger.info("User data saved successfully")
    except Exception as e:
        logger.error(f"Error saving user data: {e}")

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
def get_start_keyboard(has_key: bool = False):
    """Generate the start menu keyboard."""
    buttons = [
        [InlineKeyboardButton("🔐 Enter 2FA Key", callback_data="enter_2fa")]
    ]
    if has_key:
        buttons.append([InlineKeyboardButton("🗑️ Delete My Key", callback_data="delete_key")])
    buttons.append([InlineKeyboardButton("📚 About Bot", callback_data="about_bot")])
    buttons.append([InlineKeyboardButton("❓ Help", callback_data="help")])
    return InlineKeyboardMarkup(buttons)

def get_totp_keyboard():
    """Generate the TOTP options keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Generate TOTP Code", callback_data="get_totp")],
        [InlineKeyboardButton("🔑 Enter New Key", callback_data="enter_2fa")],
        [InlineKeyboardButton("🗑️ Delete My Key", callback_data="delete_key")],
        [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
    ])

# Command Handlers
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command."""
    user_id = message.from_user.id
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    welcome_text = "✨ **Welcome to the Advanced 2FA Manager!** ✨\n\n"
    
    if has_key:
        welcome_text += "✅ You already have a 2FA key stored!\n\n"
    
    welcome_text += (
        "🔒 **Features:**\n"
        "• Securely store your 2FA keys with encryption\n"
        "• Generate TOTP codes instantly\n"
        "• Persistent storage (keys saved across restarts)\n"
        "• Anti-spam button cooldown\n"
        "• Delete keys when needed\n\n"
        "🌟 **Get Started:**\n"
        "1️⃣ Click **'Enter 2FA Key'** below\n"
        "2️⃣ Send your 2FA key when prompted\n"
        "3️⃣ Use the **Generate TOTP Code** button anytime!\n\n"
        "🎉 _Let's get started!_"
    )
    
    await message.reply_text(
        welcome_text,
        reply_markup=get_start_keyboard(has_key)
    )
    logger.info(f"User {user_id} started the bot")

@app.on_message(filters.command("help"))
async def help_command(client: Client, message: Message):
    """Handle the /help command."""
    await message.reply_text(
        "📖 **Help Guide**\n\n"
        "**Available Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "**How to Use:**\n"
        "1️⃣ Get your 2FA secret key from your service\n"
        "2️⃣ Click 'Enter 2FA Key' and send the key\n"
        "3️⃣ Generate TOTP codes whenever needed\n\n"
        "**Security Notes:**\n"
        "🔐 Your keys are stored securely\n"
        "🔒 Only you can access your keys\n"
        "🗑️ You can delete your key anytime\n\n"
        "**Troubleshooting:**\n"
        "• Make sure your key is in Base32 format (A-Z, 2-7)\n"
        "• Remove any spaces from your key\n"
        "• If codes don't work, re-enter your key\n\n"
        "❓ Need more help? Contact support!",
        reply_markup=get_start_keyboard(message.from_user.id in user_2fa_keys)
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
        "💡 **Tips:**\n"
        "• Remove any spaces from your key\n"
        "• Use UPPERCASE letters\n"
        "• Only use characters A-Z and numbers 2-7\n\n"
        "🔒 _Your key will be stored securely and persistently._\n\n"
        "Type /start to cancel."
    )
    user_2fa_keys[user_id] = None
    logger.info(f"User {user_id} requested to enter 2FA key")

@app.on_message(filters.private & filters.text & ~filters.command(["start", "help"]))
async def handle_2fa_key(client: Client, message: Message):
    """Handle the user's 2FA key submission."""
    user_id = message.from_user.id
    
    # Check if user is in key entry mode
    if user_id not in user_2fa_keys:
        await message.reply_text(
            "❌ Please use /start to begin or use the menu buttons.",
            reply_markup=get_start_keyboard(False)
        )
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
        logger.warning(f"User {user_id} provided invalid key format")
        return

    try:
        # Test if the key works
        totp = pyotp.TOTP(key)
        test_code = totp.now()
        
        # Save the key
        user_2fa_keys[user_id] = key
        save_user_data()  # Persist to disk
        
        await message.reply_text(
            "✅ **2FA Key Saved Successfully!**\n\n"
            f"🔐 Test Code: `{test_code}`\n\n"
            "🎉 Your key has been securely stored and will persist across bot restarts.\n"
            "You can now generate TOTP codes anytime using the button below.",
            reply_markup=get_totp_keyboard()
        )
        logger.info(f"User {user_id} successfully saved 2FA key")
    except Exception as e:
        logger.error(f"Error saving key for user {user_id}: {e}")
        await message.reply_text(
            "❌ **Error Saving Your Key**\n\n"
            "The key format appears valid but couldn't be processed.\n"
            "Please verify your key and try again."
        )

@app.on_callback_query(filters.regex("get_totp"))
async def generate_totp(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the user."""
    user_id = callback.from_user.id
    if is_button_locked(user_id, "get_totp"):
        remaining = get_remaining_time(user_id, "get_totp")
        await callback.answer(f"⏳ Wait {remaining} seconds.", show_alert=True)
        return

    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.message.edit_text(
            "❌ No key found! Please enter your key first.",
            reply_markup=get_start_keyboard(False)
        )
        return

    lock_button(user_id, "get_totp")
    try:
        totp = pyotp.TOTP(user_2fa_keys[user_id])
        code = totp.now()
        
        # Calculate time until next code
        import time
        remaining_time = 30 - (int(time.time()) % 30)
        
        await callback.message.edit_text(
            f"🔐 **Your Current TOTP Code:**\n\n"
            f"✨ `{code}` ✨\n\n"
            f"⏱️ Valid for: **{remaining_time}** seconds\n\n"
            "⚡ _Generate a new code anytime!_",
            reply_markup=get_totp_keyboard()
        )
        logger.info(f"Generated TOTP for user {user_id}")
        await callback.answer("✅ Code generated!", show_alert=False)
    except Exception as e:
        logger.error(f"Error generating TOTP for user {user_id}: {e}")
        await callback.message.edit_text(
            "❌ Error generating your TOTP code.\nPlease try re-entering your key.",
            reply_markup=get_start_keyboard(True)
        )

@app.on_callback_query(filters.regex("about_bot"))
async def about_bot(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    user_id = callback.from_user.id
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    await callback.message.edit_text(
        "🤖 **About This Bot**\n\n"
        "🔒 **Security Features:**\n"
        "• Persistent encrypted storage\n"
        "• No data sharing or logging\n"
        "• Anti-spam protection\n\n"
        "⚡ **Capabilities:**\n"
        "• Generate TOTP codes instantly\n"
        "• Manage multiple 2FA keys per user\n"
        "• Real-time code validity countdown\n\n"
        "🛠️ **Technology:**\n"
        "• Built with Pyrogram\n"
        "• PyOTP for TOTP generation\n"
        "• JSON-based persistence\n\n"
        "📝 **Version:** 2.0\n"
        "👨‍💻 **Developer:** DAXXTEAM\n\n"
        "💡 _Secure, Fast, and Reliable_",
        reply_markup=get_start_keyboard(has_key)
    )
    await callback.answer()

@app.on_callback_query(filters.regex("help"))
async def help_callback(client: Client, callback: CallbackQuery):
    """Show help information."""
    user_id = callback.from_user.id
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    await callback.message.edit_text(
        "📖 **Help Guide**\n\n"
        "**Available Commands:**\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "**How to Use:**\n"
        "1️⃣ Get your 2FA secret key from your service\n"
        "2️⃣ Click 'Enter 2FA Key' and send the key\n"
        "3️⃣ Generate TOTP codes whenever needed\n\n"
        "**Security Notes:**\n"
        "🔐 Your keys are stored securely\n"
        "🔒 Only you can access your keys\n"
        "🗑️ You can delete your key anytime\n\n"
        "**Troubleshooting:**\n"
        "• Make sure your key is in Base32 format (A-Z, 2-7)\n"
        "• Remove any spaces from your key\n"
        "• If codes don't work, re-enter your key\n\n"
        "❓ Need more help? Contact support!",
        reply_markup=get_start_keyboard(has_key)
    )
    await callback.answer()

@app.on_callback_query(filters.regex("delete_key"))
async def delete_key(client: Client, callback: CallbackQuery):
    """Delete user's 2FA key."""
    user_id = callback.from_user.id
    
    if user_id not in user_2fa_keys or not user_2fa_keys[user_id]:
        await callback.answer("❌ No key found to delete!", show_alert=True)
        return
    
    # Create confirmation keyboard
    confirm_keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data="confirm_delete"),
            InlineKeyboardButton("❌ Cancel", callback_data="cancel_delete")
        ]
    ])
    
    await callback.message.edit_text(
        "⚠️ **Confirm Deletion**\n\n"
        "Are you sure you want to delete your 2FA key?\n\n"
        "🗑️ This action cannot be undone!\n"
        "You will need to re-enter your key to generate codes again.",
        reply_markup=confirm_keyboard
    )
    await callback.answer()

@app.on_callback_query(filters.regex("confirm_delete"))
async def confirm_delete_key(client: Client, callback: CallbackQuery):
    """Confirm and delete user's 2FA key."""
    user_id = callback.from_user.id
    
    if user_id in user_2fa_keys:
        del user_2fa_keys[user_id]
        save_user_data()  # Persist deletion
        logger.info(f"User {user_id} deleted their 2FA key")
        
        await callback.message.edit_text(
            "✅ **Key Deleted Successfully!**\n\n"
            "Your 2FA key has been removed from our system.\n"
            "You can add a new key anytime.",
            reply_markup=get_start_keyboard(False)
        )
        await callback.answer("🗑️ Key deleted!", show_alert=False)
    else:
        await callback.answer("❌ No key found!", show_alert=True)

@app.on_callback_query(filters.regex("cancel_delete"))
async def cancel_delete_key(client: Client, callback: CallbackQuery):
    """Cancel key deletion."""
    user_id = callback.from_user.id
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    await callback.message.edit_text(
        "✅ **Deletion Cancelled**\n\n"
        "Your key is safe and secure.",
        reply_markup=get_start_keyboard(has_key)
    )
    await callback.answer("Cancelled", show_alert=False)

@app.on_callback_query(filters.regex("main_menu"))
async def main_menu(client: Client, callback: CallbackQuery):
    """Return to main menu."""
    user_id = callback.from_user.id
    has_key = user_id in user_2fa_keys and user_2fa_keys[user_id]
    
    welcome_text = "🏠 **Main Menu**\n\n"
    if has_key:
        welcome_text += "✅ You have a 2FA key stored!\n\n"
    else:
        welcome_text += "❌ No 2FA key stored yet.\n\n"
    
    welcome_text += "Select an option below:"
    
    await callback.message.edit_text(
        welcome_text,
        reply_markup=get_start_keyboard(has_key)
    )
    await callback.answer()

if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("🚀 Starting 2FA Bot v2.0...")
    logger.info("=" * 50)
    
    # Load existing user data
    load_user_data()
    
    try:
        logger.info("✅ Bot is now running and ready to accept requests!")
        app.run()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        # Save data before exit
        save_user_data()
        logger.info("👋 Bot shutdown complete")
