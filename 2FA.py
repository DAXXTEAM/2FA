import os
from pyrogram import Client, filters
from pyrogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
import pyotp
import re
from time import time
from typing import Dict, Tuple, List

# Configuration from Environment Variables
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure credentials are set
if not all([API_ID, API_HASH, BOT_TOKEN]):
    raise ValueError("API_ID, API_HASH, and BOT_TOKEN must be set in environment variables.")

API_ID = int(API_ID)

# Initialize Bot
app = Client("2FA_Bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Constants
BUTTON_COOLDOWN = 5  # seconds (reduced for better UX)
TOTP_INTERVAL = 30  # TOTP refresh interval

# Storage
user_2fa_keys: Dict[int, List[Dict[str, str]]] = {}  # {user_id: [{"name": "...", "key": "..."}]}
user_states: Dict[int, str] = {}  # Track user input states
button_locks: Dict[Tuple[int, str], float] = {}


# Helper Functions
def is_valid_base32(s: str) -> bool:
    """Check if the string is valid Base32."""
    base32_pattern = r"^[A-Z2-7]+=*$"
    s = s.replace(" ", "").upper()
    return bool(re.match(base32_pattern, s)) and len(s) >= 16


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
    """Get remaining seconds until TOTP code changes."""
    return TOTP_INTERVAL - (int(time()) % TOTP_INTERVAL)


def generate_time_bar(remaining: int) -> str:
    """Generate a visual progress bar for TOTP expiry."""
    total_blocks = 10
    filled = int((remaining / TOTP_INTERVAL) * total_blocks)
    empty = total_blocks - filled
    return "█" * filled + "░" * empty


# Keyboards
def get_start_keyboard():
    """Generate the start menu keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔐 Add 2FA Key", callback_data="add_2fa")],
        [InlineKeyboardButton("📋 My Keys", callback_data="list_keys")],
        [InlineKeyboardButton("📚 About Bot", callback_data="about_bot")]
    ])


def get_totp_keyboard(key_index: int = 0):
    """Generate the TOTP options keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Code", callback_data=f"get_totp_{key_index}")],
        [InlineKeyboardButton("📋 My Keys", callback_data="list_keys")],
        [InlineKeyboardButton("🏠 Home", callback_data="home")]
    ])


def get_keys_keyboard(user_id: int):
    """Generate keyboard with user's saved keys."""
    buttons = []
    keys = user_2fa_keys.get(user_id, [])
    
    for i, key_data in enumerate(keys):
        name = key_data.get("name", f"Key {i+1}")
        buttons.append([
            InlineKeyboardButton(f"🔑 {name}", callback_data=f"get_totp_{i}"),
            InlineKeyboardButton("🗑️", callback_data=f"delete_key_{i}")
        ])
    
    buttons.append([InlineKeyboardButton("➕ Add New Key", callback_data="add_2fa")])
    buttons.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    
    return InlineKeyboardMarkup(buttons)


def get_back_keyboard():
    """Generate back button keyboard."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Home", callback_data="home")]
    ])


def get_confirm_delete_keyboard(key_index: int):
    """Generate confirmation keyboard for key deletion."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Yes, Delete", callback_data=f"confirm_delete_{key_index}"),
            InlineKeyboardButton("❌ Cancel", callback_data="list_keys")
        ]
    ])


# Command Handlers
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Handle the /start command."""
    user_id = message.from_user.id
    user_states.pop(user_id, None)  # Clear any pending states
    
    await message.reply_text(
        "✨ **Welcome to 2FA Manager Bot!** ✨\n\n"
        "🔒 **Features:**\n"
        "• Store multiple 2FA keys securely\n"
        "• Generate TOTP codes instantly\n"
        "• Visual countdown timer\n"
        "• Easy key management\n\n"
        "🌟 **Get Started:**\n"
        "1️⃣ Click **'Add 2FA Key'** below\n"
        "2️⃣ Give your key a name (e.g., 'Gmail')\n"
        "3️⃣ Send your 2FA secret key\n"
        "4️⃣ Generate codes anytime!\n\n"
        "📌 Use /help for more commands",
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
        "• /keys - List your saved keys\n"
        "• /add - Add a new 2FA key\n\n"
        "**How to use:**\n"
        "1. Get your 2FA secret key from the service\n"
        "2. Add it to the bot with a memorable name\n"
        "3. Generate TOTP codes when needed\n\n"
        "**Tips:**\n"
        "• TOTP codes change every 30 seconds\n"
        "• Watch the countdown bar for timing\n"
        "• Keep your secret keys safe!\n\n"
        "⚠️ **Note:** Keys are stored in memory only. "
        "They will be lost if the bot restarts.",
        reply_markup=get_back_keyboard()
    )


@app.on_message(filters.command("keys"))
async def keys_command(client: Client, message: Message):
    """Handle the /keys command."""
    user_id = message.from_user.id
    keys = user_2fa_keys.get(user_id, [])
    
    if not keys:
        await message.reply_text(
            "📭 **No Keys Found**\n\n"
            "You haven't added any 2FA keys yet.\n"
            "Click the button below to add one!",
            reply_markup=get_start_keyboard()
        )
        return
    
    await message.reply_text(
        f"🔐 **Your 2FA Keys** ({len(keys)} saved)\n\n"
        "Select a key to generate its TOTP code:",
        reply_markup=get_keys_keyboard(user_id)
    )


@app.on_message(filters.command("add"))
async def add_command(client: Client, message: Message):
    """Handle the /add command."""
    user_id = message.from_user.id
    user_states[user_id] = "awaiting_name"
    
    await message.reply_text(
        "📝 **Add New 2FA Key**\n\n"
        "**Step 1:** Enter a name for this key\n"
        "_(e.g., Gmail, Discord, GitHub)_",
        reply_markup=get_back_keyboard()
    )


# Callback Handlers
@app.on_callback_query(filters.regex("^home$"))
async def home_callback(client: Client, callback: CallbackQuery):
    """Handle home button."""
    user_id = callback.from_user.id
    user_states.pop(user_id, None)
    
    await callback.message.edit_text(
        "✨ **2FA Manager Bot** ✨\n\n"
        "🔒 Securely manage your 2FA keys\n\n"
        "Select an option below:",
        reply_markup=get_start_keyboard()
    )


@app.on_callback_query(filters.regex("^add_2fa$"))
async def add_2fa_callback(client: Client, callback: CallbackQuery):
    """Prompt user to add a new 2FA key."""
    user_id = callback.from_user.id
    
    if is_button_locked(user_id, "add_2fa"):
        remaining = get_remaining_time(user_id, "add_2fa")
        await callback.answer(f"⏳ Wait {remaining}s", show_alert=True)
        return
    
    lock_button(user_id, "add_2fa")
    user_states[user_id] = "awaiting_name"
    
    await callback.message.edit_text(
        "📝 **Add New 2FA Key**\n\n"
        "**Step 1:** Enter a name for this key\n"
        "_(e.g., Gmail, Discord, GitHub)_",
        reply_markup=get_back_keyboard()
    )


@app.on_callback_query(filters.regex("^list_keys$"))
async def list_keys_callback(client: Client, callback: CallbackQuery):
    """Show user's saved keys."""
    user_id = callback.from_user.id
    user_states.pop(user_id, None)
    keys = user_2fa_keys.get(user_id, [])
    
    if not keys:
        await callback.message.edit_text(
            "📭 **No Keys Found**\n\n"
            "You haven't added any 2FA keys yet.\n"
            "Click the button below to add one!",
            reply_markup=get_start_keyboard()
        )
        return
    
    await callback.message.edit_text(
        f"🔐 **Your 2FA Keys** ({len(keys)} saved)\n\n"
        "Select a key to generate its TOTP code\n"
        "or tap 🗑️ to delete:",
        reply_markup=get_keys_keyboard(user_id)
    )


@app.on_callback_query(filters.regex(r"^get_totp_(\d+)$"))
async def generate_totp_callback(client: Client, callback: CallbackQuery):
    """Generate a TOTP code for the selected key."""
    user_id = callback.from_user.id
    key_index = int(callback.data.split("_")[-1])
    
    keys = user_2fa_keys.get(user_id, [])
    
    if not keys or key_index >= len(keys):
        await callback.message.edit_text(
            "❌ **Key Not Found**\n\n"
            "This key may have been deleted.",
            reply_markup=get_start_keyboard()
        )
        return
    
    key_data = keys[key_index]
    key_name = key_data.get("name", f"Key {key_index + 1}")
    secret_key = key_data.get("key")
    
    try:
        totp = pyotp.TOTP(secret_key)
        code = totp.now()
        remaining = get_totp_remaining_seconds()
        time_bar = generate_time_bar(remaining)
        
        await callback.message.edit_text(
            f"🔐 **{key_name}**\n\n"
            f"┌────────────────────┐\n"
            f"│    `{code}`    │\n"
            f"└────────────────────┘\n\n"
            f"⏱️ **Expires in:** {remaining}s\n"
            f"[{time_bar}]\n\n"
            f"💡 _Tap refresh before it expires!_",
            reply_markup=get_totp_keyboard(key_index)
        )
        await callback.answer()
    except Exception as e:
        await callback.message.edit_text(
            f"❌ **Error generating code**\n\n"
            f"There was a problem with this key.\n"
            f"You may need to re-add it.",
            reply_markup=get_keys_keyboard(user_id)
        )


@app.on_callback_query(filters.regex(r"^delete_key_(\d+)$"))
async def delete_key_callback(client: Client, callback: CallbackQuery):
    """Confirm key deletion."""
    user_id = callback.from_user.id
    key_index = int(callback.data.split("_")[-1])
    
    keys = user_2fa_keys.get(user_id, [])
    
    if not keys or key_index >= len(keys):
        await callback.answer("Key not found!", show_alert=True)
        return
    
    key_name = keys[key_index].get("name", f"Key {key_index + 1}")
    
    await callback.message.edit_text(
        f"🗑️ **Delete Key?**\n\n"
        f"Are you sure you want to delete:\n"
        f"**{key_name}**\n\n"
        f"⚠️ _This action cannot be undone!_",
        reply_markup=get_confirm_delete_keyboard(key_index)
    )


@app.on_callback_query(filters.regex(r"^confirm_delete_(\d+)$"))
async def confirm_delete_callback(client: Client, callback: CallbackQuery):
    """Delete the confirmed key."""
    user_id = callback.from_user.id
    key_index = int(callback.data.split("_")[-1])
    
    keys = user_2fa_keys.get(user_id, [])
    
    if not keys or key_index >= len(keys):
        await callback.answer("Key not found!", show_alert=True)
        return
    
    key_name = keys[key_index].get("name", f"Key {key_index + 1}")
    del keys[key_index]
    
    await callback.answer(f"✅ {key_name} deleted!", show_alert=True)
    
    # Show updated key list
    if keys:
        await callback.message.edit_text(
            f"🔐 **Your 2FA Keys** ({len(keys)} saved)\n\n"
            "Select a key to generate its TOTP code:",
            reply_markup=get_keys_keyboard(user_id)
        )
    else:
        await callback.message.edit_text(
            "📭 **No Keys Left**\n\n"
            "All your keys have been deleted.\n"
            "Add a new key to continue!",
            reply_markup=get_start_keyboard()
        )


@app.on_callback_query(filters.regex("^about_bot$"))
async def about_bot_callback(client: Client, callback: CallbackQuery):
    """Show information about the bot."""
    await callback.message.edit_text(
        "🤖 **About 2FA Manager Bot**\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔒 **What it does:**\n"
        "Securely manage your 2FA keys and generate\n"
        "TOTP (Time-based One-Time Password) codes.\n\n"
        "✨ **Features:**\n"
        "• Multiple keys support\n"
        "• Visual countdown timer\n"
        "• Easy key management\n"
        "• Anti-spam protection\n\n"
        "🛠️ **Built with:**\n"
        "• Python + Pyrogram\n"
        "• PyOTP Library\n\n"
        "📌 **Version:** 2.0\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━",
        reply_markup=get_start_keyboard()
    )


# Message Handler for User Input
@app.on_message(filters.private & filters.text & ~filters.command(["start", "help", "keys", "add"]))
async def handle_text_input(client: Client, message: Message):
    """Handle user text input based on current state."""
    user_id = message.from_user.id
    state = user_states.get(user_id)
    
    if state == "awaiting_name":
        # User is entering a name for the key
        key_name = message.text.strip()[:50]  # Limit name length
        
        if not key_name:
            await message.reply_text(
                "❌ **Invalid Name**\n\n"
                "Please enter a valid name for your key.",
                reply_markup=get_back_keyboard()
            )
            return
        
        user_states[user_id] = f"awaiting_key:{key_name}"
        
        await message.reply_text(
            f"✅ **Name:** {key_name}\n\n"
            "**Step 2:** Now send your 2FA secret key\n\n"
            "➡️ The key must be a valid Base32 string\n"
            "📋 Example: `JBSWY3DPEHPK3PXP`\n\n"
            "🔒 _Your key will be stored securely_",
            reply_markup=get_back_keyboard()
        )
    
    elif state and state.startswith("awaiting_key:"):
        # User is entering the 2FA key
        key_name = state.split(":", 1)[1]
        secret_key = message.text.strip().replace(" ", "").upper()
        
        # Delete the message containing the secret key for security
        try:
            await message.delete()
        except Exception:
            pass
        
        if not is_valid_base32(secret_key):
            await message.reply_text(
                "🚫 **Invalid Key!**\n\n"
                "Make sure your key follows the Base32 format:\n"
                "• Only letters A-Z and digits 2-7\n"
                "• Minimum 16 characters\n"
                "• No special characters\n\n"
                "📋 Example: `JBSWY3DPEHPK3PXP`\n\n"
                "ℹ️ _Try again or tap Home to cancel_",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Validate the key can generate TOTP
        try:
            pyotp.TOTP(secret_key).now()
        except Exception:
            await message.reply_text(
                "❌ **Invalid 2FA Key**\n\n"
                "This key cannot generate TOTP codes.\n"
                "Please check and try again.",
                reply_markup=get_back_keyboard()
            )
            return
        
        # Save the key
        if user_id not in user_2fa_keys:
            user_2fa_keys[user_id] = []
        
        user_2fa_keys[user_id].append({
            "name": key_name,
            "key": secret_key
        })
        
        user_states.pop(user_id, None)
        key_index = len(user_2fa_keys[user_id]) - 1
        
        await message.reply_text(
            f"✅ **Key Saved Successfully!**\n\n"
            f"🔑 **Name:** {key_name}\n\n"
            f"🎉 You can now generate TOTP codes!",
            reply_markup=get_totp_keyboard(key_index)
        )
    
    else:
        # No active state, show help
        await message.reply_text(
            "👋 **Hi there!**\n\n"
            "Use /start to begin or /help for commands.",
            reply_markup=get_start_keyboard()
        )


if __name__ == "__main__":
    print("🚀 2FA Bot is now running...")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📌 Make sure you have set:")
    print("   • API_ID")
    print("   • API_HASH") 
    print("   • BOT_TOKEN")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    app.run()
