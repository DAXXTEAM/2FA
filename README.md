# 🔐 2FA Manager Bot

A **Telegram 2FA verification bot** that generates TOTP (Time-based One-Time Password) codes securely. Supports deployment on **VPS** and **Heroku**.

## ✨ Features

- 🔒 **Secure 2FA code generation** via Telegram
- ⏱️ **Time remaining indicator** for each code
- 🛡️ **Anti-spam protection** with cooldowns
- 🗑️ **Delete key** functionality
- 📱 **Inline buttons** for easy navigation
- 🚀 **VPS & Heroku** deployment support

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Show help and usage guide |
| `/totp` | Quickly generate your TOTP code |

---

## 🚀 Deployment Guide

### 1️⃣ Deploy on Heroku

[![Deploy on Heroku](https://img.shields.io/badge/Deploy%20On%20Heroku-purple?style=for-the-badge&logo=heroku)](https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA)

**Step 1:** Click the deploy button above

**Step 2:** Set Environment Variables:
- `API_ID` → Your Telegram API ID
- `API_HASH` → Your Telegram API Hash
- `BOT_TOKEN` → Your Telegram Bot Token

**Step 3:** Deploy & enable the worker dyno in **Resources**

---

### 2️⃣ Deploy on VPS

**Step 1:** Install Dependencies
```bash
sudo apt update && sudo apt install -y python3 python3-pip git
```

**Step 2:** Clone the Repository
```bash
git clone https://github.com/DAXXTEAM/2FA.git && cd 2FA
```

**Step 3:** Install Python Requirements
```bash
pip3 install -r requirements.txt
```

**Step 4:** Set Environment Variables
```bash
export API_ID='your-api-id'
export API_HASH='your-api-hash'
export BOT_TOKEN='your-bot-token'
```

**Step 5:** Run the Bot
```bash
python3 2FA.py
```

---

## 🔧 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | ✅ Yes |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | ✅ Yes |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) | ✅ Yes |

---

## 📦 Dependencies

- **Pyrogram** - Telegram MTProto API framework
- **PyOTP** - Python One-Time Password library
- **TgCrypto** - Fast cryptography for Pyrogram

---

## ⚠️ Security Notice

- Keys are stored **in memory only** and will be lost on bot restart
- The bot automatically deletes messages containing your secret key (when possible)
- Never share your 2FA secret keys with anyone

---

## 📜 License

This project is open-source and available under the **MIT License**.

## 📞 Contact & Support

- GitHub: [DAXXTEAM](https://github.com/DAXXTEAM/2FA)
- Telegram: [Support Group](https://t.me/vlubtech)
