# 🔐 2FA Manager Bot

A **Telegram 2FA verification bot** that helps users securely manage their two-factor authentication codes. Generate TOTP codes instantly with a beautiful, user-friendly interface.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Storage** | Store your 2FA keys safely in memory |
| ⚡ **Instant Generation** | Generate TOTP codes with one click |
| ⏱️ **Expiry Countdown** | Visual countdown showing code validity |
| 🛡️ **Anti-Spam** | Built-in cooldown to prevent abuse |
| 🗑️ **Key Management** | Easy delete and replace keys |
| 📱 **User-Friendly** | Clean, intuitive button interface |

---

## 🚀 Quick Deploy

### Deploy on Heroku

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA">
    <img src="https://img.shields.io/badge/Deploy%20to%20Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white" alt="Deploy to Heroku"/>
  </a>
</p>

**Required Environment Variables:**

| Variable | Description |
|----------|-------------|
| `API_ID` | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Your Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Your bot token from [@BotFather](https://t.me/BotFather) |

---

### Deploy on VPS

#### Prerequisites
- Python 3.8 or higher
- pip package manager

#### Step 1: Clone the Repository
```bash
git clone https://github.com/DAXXTEAM/2FA.git
cd 2FA
```

#### Step 2: Install Dependencies
```bash
pip3 install -r requirements.txt
```

#### Step 3: Set Environment Variables
```bash
export API_ID='your_api_id'
export API_HASH='your_api_hash'
export BOT_TOKEN='your_bot_token'
```

Or create a `.env` file (requires `python-dotenv`):
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
```

#### Step 4: Run the Bot
```bash
python3 2FA.py
```

---

### Run with Docker

```bash
docker run -d \
  -e API_ID=your_api_id \
  -e API_HASH=your_api_hash \
  -e BOT_TOKEN=your_bot_token \
  --name 2fa-bot \
  python:3.11-slim \
  bash -c "pip install pyrogram pyotp TgCrypto && python 2FA.py"
```

---

## 📖 Usage

1. **Start the bot** - Send `/start` to the bot
2. **Enter your 2FA key** - Click "Enter 2FA Key" and send your secret key
3. **Generate codes** - Click "Generate TOTP Code" whenever you need a code
4. **Copy the code** - Tap on the code to copy it

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Show help and usage instructions |

---

## 🔒 Security Notes

- ⚠️ **Keys are stored in memory only** - They will be lost if the bot restarts
- 🔐 **Never share your 2FA secret keys** with anyone
- 🗑️ **Delete your key** when you're done using the bot
- 🛡️ **Use at your own risk** - This bot is for convenience, not as a primary authenticator

---

## 🛠️ Technical Details

- **Framework:** [Pyrogram](https://pyrogram.org/) 2.0+
- **TOTP Library:** [PyOTP](https://pyauth.github.io/pyotp/)
- **Encryption:** TgCrypto for faster message processing
- **TOTP Interval:** 30 seconds (RFC 6238 standard)

---

## 📝 Changelog

### v2.0.0
- ✨ Added TOTP expiry countdown display
- ✨ Added delete key functionality
- ✨ Added help command and button
- 🔒 Removed hardcoded credentials
- 🎨 Improved UI with better formatting
- 🐛 Fixed duplicate client initialization
- 📝 Added logging for debugging
- ⚡ Better input validation

### v1.0.0
- Initial release

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

## 📞 Contact & Support

- **GitHub:** [DAXXTEAM/2FA](https://github.com/DAXXTEAM/2FA)
- **Telegram:** [Support Group](https://t.me/vlubtech)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/DAXXTEAM">DAXXTEAM</a>
</p>
