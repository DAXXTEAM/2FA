# 🔐 2FA Manager Bot

A **Telegram 2FA Bot** that helps users manage their two-factor authentication keys and generate TOTP codes. Supports deployment on **VPS** and **Heroku**.

## ✨ Features

- 🔑 **Multiple Keys** - Store and manage multiple 2FA keys
- ⏱️ **Visual Timer** - See countdown until code expires
- 🗑️ **Key Management** - Add, view, and delete keys easily
- 🛡️ **Anti-Spam** - Built-in cooldown protection
- 📱 **User-Friendly** - Interactive buttons and menus

---

## 🚀 Deployment Guide

### 1️⃣ Deploy on Heroku

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA">
    <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-purple?style=for-the-badge&logo=heroku" width="300"/>
  </a>
</p>

**Steps:**
1. Click the button above
2. Set the environment variables:
   - `API_ID` → Your Telegram API ID
   - `API_HASH` → Your Telegram API Hash
   - `BOT_TOKEN` → Your Telegram Bot Token
3. Click **Deploy**
4. Go to **Resources** and enable the worker dyno

---

### 2️⃣ Deploy on VPS

#### Step 1: Install Dependencies
```bash
sudo apt update && sudo apt install -y python3 python3-pip git
```

#### Step 2: Clone the Repository
```bash
git clone https://github.com/DAXXTEAM/2FA.git && cd 2FA
```

#### Step 3: Install Python Requirements
```bash
pip3 install -r requirements.txt
```

#### Step 4: Configure Environment Variables
```bash
export API_ID='your-api-id'
export API_HASH='your-api-hash'
export BOT_TOKEN='your-bot-token'
```

#### Step 5: Run the Bot
```bash
python3 2FA.py
```

---

## 📖 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot |
| `/help` | Show help guide |
| `/keys` | List your saved keys |
| `/add` | Add a new 2FA key |

---

## ⚙️ Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) | ✅ |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | ✅ |
| `BOT_TOKEN` | Bot token from [@BotFather](https://t.me/BotFather) | ✅ |

---

## ⚠️ Important Notes

- **Keys are stored in memory** - They will be lost if the bot restarts
- **Never share your 2FA secret keys** with anyone
- For persistent storage, consider adding a database

---

## 📜 License

This project is open-source and available under the **MIT License**.

## 📞 Support

- GitHub: [DAXXTEAM](https://github.com/DAXXTEAM/2FA)
- Telegram: [@vlubtech](https://t.me/vlubtech)
