# Upgrade Notes - Version 2.0

## ⚠️ IMPORTANT SECURITY NOTICE

This update includes **critical security improvements**. The old version had hardcoded credentials which is a major security risk.

## What Changed

### 🔒 Security (CRITICAL)
- **Removed all hardcoded credentials** - API_ID, API_HASH, and BOT_TOKEN are no longer in the source code
- **Environment variables required** - You MUST set these before running the bot
- **Added .gitignore** - Prevents accidental commit of sensitive data

### ✨ New Features
1. **Persistent Storage** - Your 2FA keys now survive bot restarts
2. **Delete Key Feature** - Remove stored keys when needed
3. **Help System** - Detailed in-bot help and troubleshooting
4. **TOTP Timer** - See how long your code is valid
5. **Better Logging** - Comprehensive logs for debugging

### 📦 Files Added
- `CHANGELOG.md` - Version history and changes
- `UPGRADE_NOTES.md` - This file
- `.env.example` - Environment variable template
- `.gitignore` - Protect sensitive files
- `setup.sh` - Automated setup script

## How to Upgrade

### Step 1: Backup (if needed)
```bash
# Save your current version
cp 2FA.py 2FA.py.backup
```

### Step 2: Set Environment Variables

**Option A: Quick Setup (Temporary)**
```bash
export API_ID='12345678'
export API_HASH='your-api-hash-here'
export BOT_TOKEN='your-bot-token-here'
```

**Option B: Using .env file (Recommended)**
```bash
# Copy the example
cp .env.example .env

# Edit with your values
nano .env

# Load the variables
source .env
```

**Option C: Systemd Service**
See README.md for systemd configuration

### Step 3: Update Dependencies
```bash
pip3 install -r requirements.txt --upgrade
```

Or use the setup script:
```bash
./setup.sh
```

### Step 4: Test the Bot
```bash
python3 2FA.py
```

You should see:
```
INFO:__main__:==================================================
INFO:__main__:🚀 Starting 2FA Bot v2.0...
INFO:__main__:==================================================
INFO:__main__:✅ Bot is now running and ready to accept requests!
```

## Breaking Changes

### ❌ These will NOT work anymore:
1. Running without environment variables
2. Relying on hardcoded credentials
3. Expecting keys to persist without user_data.json

### ✅ What you need to do:
1. Set up environment variables (see Step 2 above)
2. Re-add your 2FA keys (old ones were in-memory only)
3. Ensure `user_data.json` has write permissions

## Troubleshooting

### Error: "API_ID, API_HASH, and BOT_TOKEN must be set"
**Solution:** You haven't set the environment variables.
```bash
# Check if they're set
echo $API_ID
echo $API_HASH
echo $BOT_TOKEN

# If empty, set them
export API_ID='your-value'
# ... etc
```

### Error: "API_ID must be a valid integer"
**Solution:** Make sure API_ID is just numbers, no quotes in the export:
```bash
export API_ID=12345678  # Correct
# NOT: export API_ID="12345678"  # Wrong
```

### Bot starts but crashes immediately
**Solution:** Check the logs for specific error. Common issues:
- Wrong credentials
- Network/firewall issues
- Missing dependencies

### Can't find my old 2FA keys
**Solution:** The old version stored keys in memory only. You need to re-add them:
1. Start the bot with `/start`
2. Click "Enter 2FA Key"
3. Send your key again
4. This time it will be saved to `user_data.json`

## New User Data File

The bot now creates a `user_data.json` file:
```json
{
  "123456789": "JBSWY3DPEHPK3PXP"
}
```

- Keys are stored as user_id: secret_key
- File is automatically created on first use
- Automatically saved when keys are added/removed
- Loaded on bot startup

**Security Note:** This file contains sensitive data. Make sure:
- It's not committed to git (already in .gitignore)
- Proper file permissions on your server
- Regular backups

## Verification Checklist

After upgrading, verify:

- [ ] Bot starts without errors
- [ ] Environment variables are set correctly
- [ ] Can add a 2FA key
- [ ] Can generate TOTP codes
- [ ] Can delete keys
- [ ] `/help` command works
- [ ] Keys persist after bot restart
- [ ] `user_data.json` is created and updated
- [ ] No credentials in source code

## Rollback (if needed)

If you need to rollback:
```bash
# Restore backup
mv 2FA.py.backup 2FA.py

# Note: You'll lose the new features but keep the old behavior
```

## Getting Help

If you encounter issues:

1. Check the logs
2. Review this document
3. Read the README.md
4. Check GitHub issues
5. Join our Telegram support group

## Questions?

**Q: Will my old keys work?**
A: No, the old version stored keys in memory only. Re-add them.

**Q: Do I need to get new API credentials?**
A: No, use your existing credentials. Just set them as environment variables.

**Q: Is this update safe?**
A: Yes! This update IMPROVES security by removing hardcoded credentials.

**Q: Can I keep using the old version?**
A: Not recommended due to security issues, but technically yes.

**Q: Where are my keys stored now?**
A: In `user_data.json` file in the same directory as the bot.

---

**Thank you for upgrading! Your bot is now more secure and feature-rich.** 🎉
