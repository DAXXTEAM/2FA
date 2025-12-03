# 🔐 2FA Manager Bot

A **Telegram 2FA (Two-Factor Authentication) Bot** that helps you generate TOTP codes securely. Built with Python and Pyrogram.

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-green?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## ✨ Features

- 🔒 **Secure TOTP Generation** - Generate time-based one-time passwords
- ⏱️ **Live Countdown Timer** - See when your code expires
- 🛡️ **Anti-Spam Protection** - Built-in cooldown system
- 📱 **User-Friendly Interface** - Easy-to-use inline buttons
- 🚀 **Fast & Lightweight** - Optimized with TgCrypto

## 📋 Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Display help information |
| `/totp` | Quick generate TOTP code |
| `/delete` | Delete your saved 2FA key |

---

## 🚀 Deployment

### Prerequisites

- Python 3.8 or higher
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Telegram API credentials (from [my.telegram.org](https://my.telegram.org))

---

### 1️⃣ Deploy on Heroku

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA">
    <img src="https://img.shields.io/badge/Deploy%20to%20Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white" alt="Deploy to Heroku"/>
  </a>
</p>

**Steps:**
1. Click the "Deploy to Heroku" button above
2. Fill in the environment variables:
   - `API_ID` - Your Telegram API ID
   - `API_HASH` - Your Telegram API Hash
   - `BOT_TOKEN` - Your Bot Token from BotFather
3. Click "Deploy App"
4. Go to **Resources** tab and enable the worker dyno

---

### 2️⃣ Deploy on VPS/Linux

```bash
# 1. Update system and install Python
sudo apt update && sudo apt install -y python3 python3-pip git

# 2. Clone the repository
git clone https://github.com/DAXXTEAM/2FA.git
cd 2FA

# 3. Install dependencies
pip3 install -r requirements.txt

# 4. Set environment variables
export API_ID='your-api-id'
export API_HASH='your-api-hash'
export BOT_TOKEN='your-bot-token'

# 5. Run the bot
python3 2FA.py
```

#### Run with systemd (Recommended for Production)

Create a service file:

```bash
sudo nano /etc/systemd/system/2fa-bot.service
```

Add the following content:

```ini
[Unit]
Description=2FA Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/2FA
Environment="API_ID=your-api-id"
Environment="API_HASH=your-api-hash"
Environment="BOT_TOKEN=your-bot-token"
ExecStart=/usr/bin/python3 2FA.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable 2fa-bot
sudo systemctl start 2fa-bot
sudo systemctl status 2fa-bot
```

---

### 3️⃣ Deploy with Docker

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY 2FA.py .

CMD ["python", "2FA.py"]
```

Build and run:

```bash
docker build -t 2fa-bot .
docker run -d \
  -e API_ID='your-api-id' \
  -e API_HASH='your-api-hash' \
  -e BOT_TOKEN='your-bot-token' \
  --name 2fa-bot \
  2fa-bot
```

---

## 🔧 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `API_ID` | ✅ Yes | Telegram API ID from my.telegram.org |
| `API_HASH` | ✅ Yes | Telegram API Hash from my.telegram.org |
| `BOT_TOKEN` | ✅ Yes | Bot token from @BotFather |

---

## 📖 How to Use

1. **Start the bot** - Send `/start` to your bot
2. **Add your 2FA key** - Click "🔐 Enter 2FA Key" and send your secret key
3. **Generate codes** - Click "🔄 Refresh Code" to get your TOTP code
4. **Copy the code** - Tap on the code to copy it

### Where to Find Your 2FA Secret Key?

- Open your authenticator app (Google Authenticator, Authy, etc.)
- Go to account settings or "Export accounts"
- Look for "Secret key", "Setup key", or scan QR code to get the key
- The key looks like: `JBSWY3DPEHPK3PXP`

---

## ⚠️ Security Notice

- **Never share your secret key** with anyone
- Keys are stored in **memory only** and cleared on bot restart
- This bot is for **personal use** - don't use it as a public service
- Always keep backup access to your 2FA accounts

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🤝 Support

- **GitHub Issues:** [Report a bug](https://github.com/DAXXTEAM/2FA/issues)
- **Telegram:** [@vlubtech](https://t.me/vlubtech)

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/DAXXTEAM">DAXXTEAM</a>
</p>
