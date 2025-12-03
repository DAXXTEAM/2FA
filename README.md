# 2FA Verification Bot

A **Telegram 2FA verification bot** that helps users securely manage their two-factor authentication keys and generate TOTP codes. This bot supports deployment on **VPS** and **Heroku**.

## Features
- 🔐 Secure **2FA key storage** (in-memory only, not persistent)
- 🔄 **TOTP code generation** with countdown timer
- 🛡️ **Auto-delete** sensitive messages for security
- ⏱️ **Anti-spam protection** with button cooldown (30 seconds)
- ✅ **Base32 validation** for 2FA keys
- 🚀 Supports **VPS & Heroku** deployment
- 📱 Beautiful UI with inline keyboards
- 🔒 **NO HARDCODED CREDENTIALS** - Secure by design

---

## 🚀 Deployment Guide

### 1️⃣ Deploy on Heroku
#### **Step 1:** Click the Button Below
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─
</h3>

<p align="center"><a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA"> <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-green?style=for-the-badge&logo=heroku" width="520" height="138.45"/></a></p>

#### **Step 2:** Set Environment Variables
- `BOT_TOKEN` → Your Telegram Bot Token
- `API_ID` → Your Telegram API ID
- `API_HASH` → Your Telegram API Hash

#### **Step 3:** Deploy & Start Bot
- Click **Deploy** on Heroku
- After deployment, go to **Resources** and enable the bot's worker dyno.

---

### 2️⃣ Deploy on VPS
#### **Step 1:** Install Dependencies
```bash
sudo apt update && sudo apt install -y python3 python3-pip git
```

#### **Step 2:** Clone the Repository
```bash
git clone https://github.com/DAXXTEAM/2FA.git && cd 2FA
```

#### **Step 3:** Install Python Requirements
```bash
pip3 install -r requirements.txt
```

#### **Step 4:** Configure Environment Variables
**IMPORTANT:** Never hardcode credentials in the code!

Export environment variables:
```bash
export BOT_TOKEN='your-bot-token'
export API_ID='your-api-id'
export API_HASH='your-api-hash'
```

Or create a `.env` file (make sure it's in .gitignore):
```bash
echo "BOT_TOKEN=your-bot-token" > .env
echo "API_ID=your-api-id" >> .env
echo "API_HASH=your-api-hash" >> .env
source .env
```

#### **Step 5:** Run the Bot
```bash
python3 2FA.py
```

---

---

## 🔒 Security Features

### What's New in This Update:
- ✅ **Removed hardcoded credentials** - No default API keys in code
- ✅ **Auto-delete sensitive messages** - User's 2FA key messages are automatically deleted
- ✅ **Session file protection** - Added to .gitignore
- ✅ **Better error handling** - More descriptive error messages
- ✅ **TOTP countdown** - Shows remaining validity time for codes
- ✅ **Input validation** - Strict Base32 format checking
- ✅ **Single client instance** - Removed duplicate bot initialization

### Security Best Practices:
1. **Never commit credentials** - Always use environment variables
2. **Use .gitignore** - Session files and .env files are excluded
3. **Keys in memory only** - Not stored in database (restart clears all keys)
4. **Message deletion** - Sensitive key messages are auto-deleted
5. **Cooldown protection** - Prevents spam and abuse

---

## 📜 License
This project is open-source and available under the **MIT License**.

## 📞 Contact & Support
- GitHub: [DAXXTEAM](https://github.com/DAXXTEAM/2FA)
- Telegram: [Support Group](https://t.me/vlubtech)

---

## ⚠️ Important Notes
- **Security:** This bot stores 2FA keys in memory only. Keys are lost on restart.
- **Privacy:** Never share your 2FA keys with anyone.
- **Deployment:** Always set environment variables properly.
- **Testing:** Test the bot in a private chat before production use.
