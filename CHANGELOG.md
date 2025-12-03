# Changelog

## [Updated Version] - 2025-12-03

### 🔒 Security Improvements
- **CRITICAL:** Removed hardcoded API credentials (API_ID, API_HASH, BOT_TOKEN)
  - Previously had default values in code - major security risk
  - Now requires environment variables to be set
- Added auto-deletion of messages containing 2FA keys for privacy
- Added `.gitignore` to prevent accidental commit of:
  - Session files (*.session)
  - Environment files (.env)
  - Python cache files
  - IDE files

### ✨ Feature Enhancements
- Added countdown timer showing TOTP code validity (remaining seconds)
- Better user feedback with callback answers
- Improved filter on message handler to avoid conflicts with /start command
- Added check to prevent overwriting existing keys unless explicitly requested
- Enhanced "About Bot" section with security feature descriptions

### 🐛 Bug Fixes
- Removed duplicate `bot` client instance (only kept `app`)
- Fixed potential race condition in message handler
- Better exception handling with descriptive error messages
- Proper API_ID integer conversion with error handling

### 📦 Dependencies
- Updated `requirements.txt` with version pinning:
  - `pyrogram==2.0.106`
  - `TgCrypto==1.2.5` (for faster encryption)
  - `pyotp==2.9.0`

### 📝 Documentation
- Updated README.md with comprehensive security features
- Added deployment best practices
- Created `.env.example` for easy configuration
- Enhanced VPS deployment instructions
- Added security warnings and notes

### 🔧 Code Quality
- Better code organization and comments
- Consistent naming conventions
- Improved startup logging messages
- Enhanced inline documentation

---

## Migration Guide

### If you're updating from the old version:

1. **Remove any hardcoded credentials** from your code
2. **Set environment variables** before running:
   ```bash
   export API_ID=your_api_id
   export API_HASH=your_api_hash
   export BOT_TOKEN=your_bot_token
   ```
3. **Update dependencies:**
   ```bash
   pip install -r requirements.txt --upgrade
   ```
4. **Delete old session files** (they'll be regenerated):
   ```bash
   rm *.session*
   ```

---

## Breaking Changes
- Bot now **requires** environment variables - will not run without them
- No default credentials provided (this is intentional for security)

## Notes
- All 2FA keys are stored in memory only (not persistent)
- Keys are lost when bot restarts
- This is by design for maximum security
