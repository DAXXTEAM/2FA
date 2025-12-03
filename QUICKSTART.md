# ⚡ Quick Start Guide

Get your 2FA Bot running in 5 minutes!

---

## 🚀 Option 1: Heroku (Easiest)

### Step 1: Click Deploy Button
[![Deploy to Heroku](https://img.shields.io/badge/Deploy%20to%20Heroku-430098?style=for-the-badge&logo=heroku&logoColor=white)](https://dashboard.heroku.com/new?template=https://github.com/DAXXTEAM/2FA)

### Step 2: Get Your Credentials

#### Get API Credentials:
1. Go to https://my.telegram.org/apps
2. Log in with your phone number
3. Click "API Development Tools"
4. Copy your `API_ID` and `API_HASH`

#### Get Bot Token:
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the instructions
4. Copy the bot token

### Step 3: Fill in Heroku Form
```
API_ID: [paste your API ID]
API_HASH: [paste your API Hash]
BOT_TOKEN: [paste your bot token]
```

### Step 4: Deploy
1. Click "Deploy app"
2. Wait for build to complete
3. Go to "Resources" tab
4. Toggle the worker dyno ON
5. Done! 🎉

---

## 💻 Option 2: VPS/Local (5 Minutes)

### Prerequisites:
- Linux/Mac/Windows with Python 3.8+
- Git installed
- 5 minutes of your time

### Quick Commands:

```bash
# 1. Clone repository
git clone https://github.com/DAXXTEAM/2FA.git
cd 2FA

# 2. Install dependencies
pip3 install -r requirements.txt

# 3. Create .env file
cp .env.example .env

# 4. Edit .env with your credentials (use nano, vim, or any editor)
nano .env

# 5. Run the bot
python3 2FA.py
```

### Your .env file should look like:
```env
API_ID=12345678
API_HASH=abcdef1234567890abcdef1234567890
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
```

---

## 📱 Using Your Bot

### Step 1: Start the Bot
1. Find your bot in Telegram (the username you gave @BotFather)
2. Click "Start" or send `/start`

### Step 2: Add Your 2FA Key
1. Click "🔐 Enter 2FA Key" button
2. Send your 2FA key (the Base32 string from your authenticator app)
3. Bot will confirm if successful

### Step 3: Generate Codes
1. Click "🔄 Generate TOTP Code" button
2. Your 6-digit code appears
3. Copy and use it!
4. Generate new codes anytime (30 second cooldown)

---

## 🔑 Where to Find Your 2FA Key?

Your 2FA key is usually shown when you first set up 2FA on a service:

### Common Locations:
- Under the QR code (labeled "Can't scan? Enter this code manually")
- In account security settings
- Called "Secret Key" or "Manual Entry Key"
- Usually 16-32 characters: `JBSWY3DPEHPK3PXP`

### Format:
- Only contains: `A-Z` and `2-7`
- Usually 16-32 characters long
- No special characters or spaces
- Case doesn't matter (bot will convert to uppercase)

---

## ❓ Common Issues

### Bot not starting?
```bash
# Check if Python is installed
python3 --version

# Check if dependencies are installed
pip3 list | grep pyrogram

# Install dependencies again
pip3 install -r requirements.txt
```

### "Invalid Key" error?
- Make sure it's Base32 format (A-Z, 2-7 only)
- Remove any spaces
- Should be at least 16 characters
- Try copying it again

### Bot token error?
- Check token format: `1234567890:ABCdef...`
- Make sure you copied the whole token
- Get a fresh token from @BotFather if needed

### Permission denied?
```bash
# On Linux/Mac, you might need:
chmod +x 2FA.py
# or run with:
python3 2FA.py
```

---

## 🎓 Need More Help?

### Documentation:
- 📖 **Full Guide**: See [README.md](README.md)
- 🔒 **Security**: See [SECURITY.md](SECURITY.md)
- 🤝 **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)
- 📝 **Changes**: See [CHANGELOG.md](CHANGELOG.md)

### Support:
- 💬 Telegram: https://t.me/vlubtech
- 🐛 Issues: https://github.com/DAXXTEAM/2FA/issues

---

## ✅ Checklist

Before you start:
- [ ] Python 3.8+ installed
- [ ] Got API_ID and API_HASH from my.telegram.org
- [ ] Got BOT_TOKEN from @BotFather
- [ ] Cloned the repository
- [ ] Installed dependencies
- [ ] Set environment variables
- [ ] Ready to run!

---

## 🎉 That's It!

You should now have a working 2FA bot! If you encounter any issues, check the documentation or ask for help in our support group.

**Happy coding! 🚀**

---

## 🔥 Pro Tips

### Keep it Running 24/7:
**Screen (Simple):**
```bash
screen -S 2fa_bot
python3 2FA.py
# Press Ctrl+A, then D to detach
# Use 'screen -r 2fa_bot' to reattach
```

**PM2 (Advanced):**
```bash
npm install -g pm2
pm2 start 2FA.py --name 2fa-bot --interpreter python3
pm2 save
pm2 startup  # Follow instructions
```

**Systemd (Production):**
See [README.md](README.md#deploy-on-vps) for full systemd setup.

### Monitor Your Bot:
```bash
# View logs in real-time
tail -f bot.log  # if you redirect output to a file

# Or just watch the console output
python3 2FA.py
```

### Update the Bot:
```bash
git pull origin main
pip3 install --upgrade -r requirements.txt
# Restart bot
```

---

<p align="center">
  <strong>Need help? Don't hesitate to ask! 😊</strong>
</p>
