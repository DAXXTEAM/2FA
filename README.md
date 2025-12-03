# 🔐 2FA Verification Bot

A **Telegram 2FA verification bot** that helps users manage their two-factor authentication keys and generate TOTP codes on-demand. This bot supports deployment on **VPS** and **Heroku**.

## ✨ Features
- 🔒 **Secure 2FA Key Storage** - Session-based in-memory storage
- ⚡ **Instant TOTP Generation** - Generate 6-digit TOTP codes on demand
- 🛡️ **Anti-Spam Protection** - Built-in cooldown mechanism (30 seconds)
- 🔄 **Real-Time Validity** - Shows remaining time for each code
- 🗑️ **Auto-Delete Messages** - Automatically deletes messages containing keys
- 📝 **Comprehensive Logging** - Full activity logging for monitoring
- 🚀 **Modern Architecture** - Built with async/await for better performance
- 🔧 **Easy Deployment** - Supports VPS & Heroku deployment

## ⚠️ Security Notes
- **Session-based storage**: Keys are stored in memory only and are cleared when the bot restarts
- **No persistent storage**: For production use with persistent storage needs, consider implementing Redis or database storage
- **Message deletion**: The bot attempts to delete messages containing 2FA keys for security
- **Environment variables**: Never commit credentials to version control

---

## 📋 Prerequisites

Before deploying, you need to obtain:

1. **Telegram API Credentials** (from https://my.telegram.org/apps):
   - `API_ID` - Your Telegram API ID (numeric)
   - `API_HASH` - Your Telegram API Hash (32-character hexadecimal)

2. **Bot Token** (from [@BotFather](https://t.me/BotFather)):
   - Create a new bot using `/newbot` command
   - Copy the bot token provided

---

## 🚀 Deployment Guide

### 1️⃣ Deploy on Heroku

#### **Step 1:** Click the Deploy Button

<p align="center">
  <a href="https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA">
    <img src="https://img.shields.io/badge/Deploy%20On%20Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white" alt="Deploy to Heroku"/>
  </a>
</p>

#### **Step 2:** Configure Environment Variables

During deployment, you'll be asked to provide:

| Variable | Description | Required |
|----------|-------------|----------|
| `API_ID` | Your Telegram API ID | ✅ Yes |
| `API_HASH` | Your Telegram API Hash | ✅ Yes |
| `BOT_TOKEN` | Your Telegram Bot Token | ✅ Yes |

⚠️ **Important**: Do NOT use default/example values. Use your own credentials!

#### **Step 3:** Deploy & Start

1. Click **Deploy App** button
2. Wait for the build to complete
3. Go to **Resources** tab
4. Enable the worker dyno (toggle it ON)
5. Check **More** → **View Logs** to verify the bot started successfully

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
pip install --upgrade pip
pip install -r requirements.txt
```

#### **Step 5:** Configure Environment Variables

**Option A: Using .env file (Recommended)**

```bash
# Copy the example file
cp .env.example .env

# Edit with your credentials
nano .env
```

Then set your values:
```env
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=your_bot_token_here
```

**Option B: Export directly (Temporary)**

```bash
export API_ID='12345678'
export API_HASH='your_api_hash_here'
export BOT_TOKEN='your_bot_token_here'
```

#### **Step 6:** Run the Bot

**Foreground (Testing):**
```bash
python3 2FA.py
```

**Background (Production with screen):**
```bash
screen -S 2fa_bot
python3 2FA.py
# Press Ctrl+A then D to detach
# Use 'screen -r 2fa_bot' to reattach
```

**Background (Production with systemd):**

Create a service file:
```bash
sudo nano /etc/systemd/system/2fa-bot.service
```

Add the following content (adjust paths as needed):
```ini
[Unit]
Description=2FA Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/2FA
Environment="API_ID=12345678"
Environment="API_HASH=your_api_hash"
Environment="BOT_TOKEN=your_token"
ExecStart=/path/to/2FA/venv/bin/python3 /path/to/2FA/2FA.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable 2fa-bot
sudo systemctl start 2fa-bot

# Check status
sudo systemctl status 2fa-bot

# View logs
sudo journalctl -u 2fa-bot -f
```

---

## 📱 How to Use

### For End Users

1. **Start the Bot**
   - Open your bot in Telegram
   - Send `/start` command
   - You'll see the welcome message with buttons

2. **Add Your 2FA Key**
   - Click "🔐 Enter 2FA Key" button
   - Send your Base32 2FA key
   - The bot will validate and save it

3. **Generate TOTP Codes**
   - Click "🔄 Generate TOTP Code" button
   - Your 6-digit code will appear
   - Code validity time is shown
   - Generate new codes as needed

4. **Get Help**
   - Send `/help` command for detailed instructions

### Supported 2FA Key Format

- **Base32 encoded** string
- Contains only: `A-Z` and `2-7`
- Usually **16-32 characters** long
- Example: `JBSWY3DPEHPK3PXP`

Where to find your 2FA key:
- Usually shown when setting up 2FA
- Often displayed as a QR code with text underneath
- Sometimes called "secret key" or "manual entry key"

---

## 🔧 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |
| `/help` | Display help information and usage guide |

---

## 🛠️ Development

### Local Development Setup

1. Clone and enter directory:
```bash
git clone https://github.com/DAXXTEAM/2FA.git
cd 2FA
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the bot:
```bash
python3 2FA.py
```

### Project Structure

```
2FA/
├── 2FA.py              # Main bot application
├── requirements.txt    # Python dependencies
├── Procfile           # Heroku process file
├── app.json           # Heroku app configuration
├── .env.example       # Environment variables template
├── .gitignore         # Git ignore rules
└── README.md          # This file
```

---

## 🔒 Security Best Practices

1. **Never commit credentials** to version control
2. **Use environment variables** for sensitive data
3. **Keep dependencies updated** regularly
4. **Monitor bot logs** for suspicious activity
5. **Implement rate limiting** (built-in cooldown)
6. **Consider persistent storage** for production use
7. **Use HTTPS** for webhook deployments (if applicable)

---

## ⚙️ Configuration

### Environment Variables

All configuration is done through environment variables:

```env
# Required
API_ID=12345678                              # Your Telegram API ID
API_HASH=abcdef1234567890abcdef1234567890   # Your Telegram API Hash
BOT_TOKEN=1234567890:ABCdef...              # Your Bot Token
```

### Customization

You can customize the bot by modifying `2FA.py`:

- `BUTTON_COOLDOWN` (line 48): Adjust cooldown time (default: 30 seconds)
- Keyboard layouts: Modify `get_start_keyboard()` and `get_totp_keyboard()`
- Messages: Update text in command handlers

---

## 🐛 Troubleshooting

### Bot not starting?

1. **Check credentials**: Ensure all environment variables are set correctly
2. **Check logs**: Look for error messages in the console or logs
3. **Verify bot token**: Test with @BotFather if needed
4. **Check API credentials**: Verify at https://my.telegram.org/apps

### "Invalid 2FA Key" error?

1. Ensure the key is **Base32 format** (A-Z, 2-7 only)
2. Remove any **spaces or special characters**
3. Key should be at least **16 characters long**
4. Try getting a fresh key from your 2FA provider

### Cooldown too long?

- Default cooldown is **30 seconds** to prevent spam
- You can adjust `BUTTON_COOLDOWN` in `2FA.py` (not recommended below 10 seconds)

### Bot stops after restart?

- Keys are stored **in memory only**
- They will be cleared when the bot restarts
- Users need to re-enter their keys after restart
- For persistent storage, consider implementing Redis or a database

---

## 📊 Features Roadmap

- [ ] Persistent storage (Redis/SQLite)
- [ ] Multiple 2FA keys per user
- [ ] Key encryption at rest
- [ ] Backup codes generation
- [ ] Multi-language support
- [ ] Admin panel
- [ ] Usage statistics

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
- **Issues**: [GitHub Issues](https://github.com/DAXXTEAM/2FA/issues)

---

## ⚠️ Disclaimer

This bot is provided as-is for educational and convenience purposes. Users are responsible for:
- Keeping their credentials secure
- Understanding the security implications of storing 2FA keys
- Complying with their service providers' terms of service
- Using the bot at their own risk

**Note**: Always use strong, unique passwords in addition to 2FA for maximum security.

---

## 🌟 Star History

If you find this project useful, please consider giving it a star ⭐ on GitHub!

---

<p align="center">Made with ❤️ for the Telegram community</p>
