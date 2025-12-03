# 🔐 Advanced 2FA Manager Bot

A **secure Telegram bot** for managing 2FA keys and generating Time-based One-Time Passwords (TOTP). Perfect for users who want quick access to their 2FA codes directly from Telegram!

## ✨ Features
- 🔒 **Secure 2FA Key Storage** - Keys stored in memory only (never saved to disk)
- ⚡ **Instant TOTP Generation** - Get your 2FA codes in seconds
- 🛡️ **Anti-Spam Protection** - Built-in cooldown system to prevent abuse
- 🎨 **Modern UI** - Clean, intuitive interface with inline keyboards
- 📱 **Multiple Commands** - Easy-to-use command system
- 🔐 **Privacy-Focused** - Your keys are never logged or stored permanently
- ⏱️ **Code Expiry Timer** - Shows remaining validity time for each code
- 📊 **Comprehensive Logging** - Track bot activity and errors

## 📋 Available Commands

- `/start` - Start the bot and see the main menu
- `/help` - Get detailed help and instructions
- `/remove` - Remove your stored 2FA key from memory

---

## 🚀 Deployment Guide

### Prerequisites
Before deploying, you need:
1. **Telegram Bot Token** - Get from [@BotFather](https://t.me/BotFather)
2. **API ID & API Hash** - Get from [my.telegram.org](https://my.telegram.org/apps)

### 1️⃣ Deploy on Heroku

#### **Step 1:** Click the Deploy Button
<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA">
    <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white" alt="Deploy to Heroku"/>
  </a>
</p>

#### **Step 2:** Configure Environment Variables
Set these **required** environment variables:
- `BOT_TOKEN` - Your Telegram Bot Token from BotFather
- `API_ID` - Your Telegram API ID from my.telegram.org
- `API_HASH` - Your Telegram API Hash from my.telegram.org

#### **Step 3:** Deploy & Enable
1. Click **Deploy** on Heroku
2. Wait for the build to complete
3. Go to **Resources** tab
4. Toggle the worker dyno to **ON**

✅ Your bot is now live!

---

### 2️⃣ Deploy on VPS (Ubuntu/Debian)

#### **Step 1:** Update System & Install Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

#### **Step 2:** Clone the Repository
```bash
git clone https://github.com/DAXXTEAM/2FA.git
cd 2FA
```

#### **Step 3:** Create Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate
```

#### **Step 4:** Install Python Requirements
```bash
pip install -r requirements.txt
```

#### **Step 5:** Set Environment Variables
Create a `.env` file or export variables:
```bash
export BOT_TOKEN='your-bot-token-here'
export API_ID='your-api-id-here'
export API_HASH='your-api-hash-here'
```

Or create a `start.sh` script:
```bash
#!/bin/bash
export BOT_TOKEN='your-bot-token-here'
export API_ID='your-api-id-here'
export API_HASH='your-api-hash-here'
python3 2FA.py
```

#### **Step 6:** Run the Bot
```bash
python3 2FA.py
```

#### **Optional: Run with systemd (Auto-restart)**
Create `/etc/systemd/system/2fa-bot.service`:
```ini
[Unit]
Description=2FA Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/2FA
Environment="BOT_TOKEN=your-token"
Environment="API_ID=your-id"
Environment="API_HASH=your-hash"
ExecStart=/usr/bin/python3 /path/to/2FA/2FA.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable 2fa-bot
sudo systemctl start 2fa-bot
sudo systemctl status 2fa-bot
```

---

## 📖 How to Use

1. **Start the bot** - Send `/start` to your bot
2. **Enter 2FA Key** - Click the button and send your Base32 2FA secret key
3. **Generate Codes** - Click "Generate TOTP Code" whenever you need a code
4. **Manage Keys** - Use `/remove` to delete your stored key

### Where to Find Your 2FA Key?
Most authenticator apps (Google Authenticator, Authy, etc.) allow you to view the secret key:
- Look for "Show key" or "Manual entry" options
- It's typically a 16-32 character Base32 string
- Example format: `JBSWY3DPEHPK3PXP`

---

## 🔒 Security Features

- **Memory-Only Storage** - Keys are stored in RAM, never written to disk
- **No Persistence** - All keys are cleared on bot restart
- **No Logging** - Secret keys are never logged
- **Anti-Spam** - 30-second cooldown prevents abuse
- **Input Validation** - Strict Base32 format checking
- **Private Only** - Bot only works in private chats

### Security Best Practices
- ⚠️ **Never share your bot token** with anyone
- ⚠️ **Don't use in public groups** - Bot is private-only by design
- ⚠️ **Keep your server secure** if self-hosting
- ⚠️ **Regularly update** dependencies for security patches

---

## 🛠️ Troubleshooting

### Bot doesn't respond
- Check if the bot is running
- Verify environment variables are set correctly
- Check logs for errors

### Invalid 2FA Key error
- Ensure the key is in Base32 format (A-Z, 2-7)
- Remove any spaces or special characters
- Key should be at least 16 characters long

### TOTP code doesn't work
- Check if your device time is synchronized
- TOTP codes expire every 30 seconds
- Verify you entered the correct secret key

### FloodWait errors
- Telegram has rate limits
- Wait for the specified time before retrying
- Bot will automatically handle this

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ Yes | Your Telegram bot token from BotFather |
| `API_ID` | ✅ Yes | Your Telegram API ID from my.telegram.org |
| `API_HASH` | ✅ Yes | Your Telegram API Hash from my.telegram.org |

### Customization

You can modify these constants in `2FA.py`:
- `BUTTON_COOLDOWN` - Cooldown time in seconds (default: 30)

---

## 📦 Dependencies

- **Pyrogram** (>=2.0.106) - Telegram MTProto API framework
- **TgCrypto** (>=1.2.5) - Cryptography library for Pyrogram
- **PyOTP** (>=2.9.0) - Python One-Time Password library

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is open-source and available under the **MIT License**.

---

## 📞 Contact & Support

- **GitHub**: [DAXXTEAM](https://github.com/DAXXTEAM/2FA)
- **Telegram**: [Support Group](https://t.me/vlubtech)
- **Issues**: [Report a bug](https://github.com/DAXXTEAM/2FA/issues)

---

## ⚠️ Disclaimer

This bot is provided as-is for educational and convenience purposes. While we implement security best practices:
- Use at your own risk
- Ensure you trust your hosting environment
- Keep backups of your 2FA keys elsewhere
- The developers are not responsible for any security breaches

---

## 🌟 Star History

If you find this project useful, please consider giving it a star! ⭐

---

**Made with ❤️ by [DAXXTEAM](https://github.com/DAXXTEAM)**
