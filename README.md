# 2FA Verification Bot v2.0

A **powerful Telegram 2FA verification bot** that helps users securely manage their two-factor authentication keys and generate TOTP codes on demand. This bot supports deployment on **VPS** and **Heroku** with enhanced security and persistence features.

## ✨ Features

### 🔒 Security
- **No hardcoded credentials** - All sensitive data via environment variables
- **Persistent storage** - Keys saved across bot restarts
- **JSON-based encryption** - Secure local storage
- **Anti-spam protection** - Button cooldown system (30 seconds)
- **Private data** - Each user's keys are isolated and secure

### ⚡ Functionality
- **Generate TOTP codes** instantly with countdown timer
- **Store multiple keys** securely
- **Delete keys** when no longer needed
- **Test codes** immediately after key entry
- **Help system** with detailed guides
- **User-friendly interface** with inline keyboards

### 🛠️ Technical
- Built with **Pyrogram 2.0**
- **PyOTP** for TOTP generation
- **Comprehensive logging** for debugging
- **Error handling** at every step
- **Type hints** for better code quality

---

## 🚀 Deployment Guide

### 1️⃣ Deploy on Heroku
#### **Step 1:** Click the Button Below
    ─「 ᴅᴇᴩʟᴏʏ ᴏɴ ʜᴇʀᴏᴋᴜ 」─
</h3>

<p align="center"><a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA"> <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-green?style=for-the-badge&logo=heroku" width="520" height="138.45"/></a></p>

#### **Step 2:** Set Environment Variables
**Required variables (no defaults for security):**
- `BOT_TOKEN` → Your Telegram Bot Token (from @BotFather)
- `API_ID` → Your Telegram API ID (from https://my.telegram.org)
- `API_HASH` → Your Telegram API Hash (from https://my.telegram.org)

**How to get credentials:**
1. **BOT_TOKEN**: Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot`
   - Follow the prompts to create your bot
   - Copy the bot token provided

2. **API_ID & API_HASH**: Visit [https://my.telegram.org](https://my.telegram.org)
   - Log in with your phone number
   - Go to "API Development Tools"
   - Create a new application
   - Copy your `api_id` and `api_hash`

#### **Step 3:** Deploy & Start Bot
- Click **Deploy** on Heroku
- After deployment, go to **Resources** and enable the bot's worker dyno
- Check the logs to ensure successful startup

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
**Option 1: Export manually (temporary):**
```bash
export BOT_TOKEN='your-bot-token-here'
export API_ID='12345678'
export API_HASH='your-api-hash-here'
```

**Option 2: Create a .env file (recommended for VPS):**
```bash
# Create .env file
cat > .env << EOF
export BOT_TOKEN='your-bot-token-here'
export API_ID='12345678'
export API_HASH='your-api-hash-here'
EOF

# Load environment variables
source .env
```

**Option 3: System-wide environment (permanent):**
```bash
# Add to ~/.bashrc or ~/.profile
echo "export BOT_TOKEN='your-bot-token-here'" >> ~/.bashrc
echo "export API_ID='12345678'" >> ~/.bashrc
echo "export API_HASH='your-api-hash-here'" >> ~/.bashrc
source ~/.bashrc
```

#### **Step 5:** Run the Bot
```bash
python3 2FA.py
```

**Run in background with nohup:**
```bash
nohup python3 2FA.py > bot.log 2>&1 &
```

**Run with systemd (recommended for production):**
```bash
# Create service file
sudo nano /etc/systemd/system/2fa-bot.service
```

Add this content:
```ini
[Unit]
Description=2FA Telegram Bot
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/2FA
Environment="BOT_TOKEN=your-token"
Environment="API_ID=12345678"
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

## 📝 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Display detailed help information |

## 🎯 Bot Features in Detail

### 1. Enter 2FA Key
- Click "Enter 2FA Key" button
- Send your Base32 secret key
- Bot validates and stores it securely
- Receive immediate test code

### 2. Generate TOTP Code
- Click "Generate TOTP Code"
- Get current 6-digit code
- See countdown timer for code validity
- Codes refresh every 30 seconds

### 3. Delete Key
- Click "Delete My Key"
- Confirm deletion
- Key removed from storage permanently

### 4. Persistent Storage
- Keys saved to `user_data.json`
- Survives bot restarts
- Automatic backup on changes

## 🔐 Security Best Practices

1. **Keep your credentials secure**
   - Never share your `BOT_TOKEN`, `API_ID`, or `API_HASH`
   - Don't commit credentials to version control
   - Use environment variables

2. **Server security**
   - Keep your VPS/server updated
   - Use firewall rules
   - Limit SSH access
   - Regular backups

3. **Bot usage**
   - Only add keys you trust
   - Delete old/unused keys
   - Don't share your bot with others
   - Use private chats only

## 🐛 Troubleshooting

### Bot won't start
```bash
# Check if environment variables are set
echo $BOT_TOKEN
echo $API_ID
echo $API_HASH

# Check Python version (needs 3.7+)
python3 --version

# Check logs
tail -f bot.log  # if running with nohup
journalctl -u 2fa-bot -f  # if running with systemd
```

### Invalid key error
- Ensure key is Base32 format (A-Z, 2-7)
- Remove all spaces and special characters
- Try uppercase only
- Get fresh key from your 2FA provider

### TOTP codes not working
- Check your device time is synced
- Verify you entered the correct key
- Try generating a new code
- Re-enter your 2FA key

## 📊 File Structure

```
2FA/
├── 2FA.py              # Main bot code
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku configuration
├── app.json           # Heroku app manifest
├── README.md          # Documentation
└── user_data.json     # User keys (created at runtime)
```

## 🔄 Updates & Changelog

### Version 2.0 (Current)
- ✅ Removed hardcoded credentials (security fix)
- ✅ Added persistent JSON storage
- ✅ Added comprehensive logging
- ✅ Added delete key feature
- ✅ Added help command
- ✅ Added countdown timer for TOTP codes
- ✅ Improved error handling
- ✅ Enhanced UI with better keyboards
- ✅ Added confirmation dialogs
- ✅ Pinned dependency versions

### Version 1.0
- Basic 2FA key storage
- TOTP code generation
- Simple inline keyboard

---

## 📜 License
This project is open-source and available under the **MIT License**.

## 📞 Contact & Support
- **GitHub**: [DAXXTEAM](https://github.com/DAXXTEAM/2FA)
- **Telegram**: [Support Group](https://t.me/vlubtech)
- **Issues**: [Report bugs](https://github.com/DAXXTEAM/2FA/issues)

## 🌟 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

> **⚠️ Security Note:** This bot stores 2FA keys. Ensure your server is secure and never share your bot token or API credentials. The bot is designed for personal use.

> **💡 Pro Tip:** For production use, consider implementing database storage (PostgreSQL/MongoDB) instead of JSON files for better scalability and security.
