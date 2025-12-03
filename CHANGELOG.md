# Changelog

All notable changes to the 2FA Bot project will be documented in this file.

## [2.0.0] - 2025-12-03

### 🔒 Security Improvements
- **CRITICAL**: Removed hardcoded API credentials from source code
  - API_ID, API_HASH, and BOT_TOKEN now require environment variables
  - No default values provided to prevent credential leakage
  - Added proper validation for credentials
- Added `.gitignore` to prevent sensitive data from being committed
- Improved input validation for 2FA keys

### ✨ New Features
- **Persistent Storage**: User 2FA keys now saved to `user_data.json`
  - Keys persist across bot restarts
  - Automatic save on key addition/deletion
  - Automatic load on bot startup
- **Delete Key Feature**: Users can now delete their stored 2FA keys
  - Confirmation dialog to prevent accidental deletion
  - Immediate persistence after deletion
- **Help Command**: Added `/help` command and help button
  - Detailed usage instructions
  - Troubleshooting guide
  - Security best practices
- **Main Menu**: New navigation option to return to main menu
- **TOTP Countdown Timer**: Shows remaining validity time for codes
- **Test Code**: Displays test TOTP code immediately after key entry

### 🛠️ Technical Improvements
- **Comprehensive Logging**: 
  - Added logging module with structured output
  - Info, warning, and error level logs
  - Better debugging capabilities
- **Better Error Handling**:
  - Try-catch blocks around all critical operations
  - User-friendly error messages
  - Graceful degradation on failures
- **Code Quality**:
  - Removed duplicate Client initialization
  - Added type hints
  - Better code organization
  - Improved function documentation
- **Dependency Management**:
  - Pinned specific versions in requirements.txt
  - Added TgCrypto for better performance
  - pyrogram==2.0.106
  - pyotp==2.9.0
  - TgCrypto==1.2.5

### 🎨 UI/UX Improvements
- Enhanced keyboard layouts with more options
- Better button organization
- Improved message formatting
- Added confirmation dialogs for destructive actions
- More informative status messages
- Better help and about text

### 📚 Documentation
- Completely rewritten README with:
  - Detailed feature list
  - Comprehensive deployment guides
  - Security best practices
  - Troubleshooting section
  - VPS deployment with systemd
  - Multiple environment variable setup methods
  - File structure documentation
  - Contributing guidelines
- Added CHANGELOG.md for version tracking
- Improved inline code comments

### 🐛 Bug Fixes
- Fixed command filter to prevent conflicts with text message handler
- Fixed keyboard display issues
- Improved session management
- Better cleanup on bot shutdown

### 🔄 Changes
- Bot session name changed from "adv_2fa_bot" to "2FA_bot"
- Removed unused `bot` Client instance
- Updated about text with version info
- Enhanced welcome messages

---

## [1.0.0] - Previous Version

### Features
- Basic 2FA key storage (in-memory only)
- TOTP code generation
- Simple inline keyboard interface
- Anti-spam cooldown system
- Basic error handling

### Issues
- ❌ Hardcoded credentials (security risk)
- ❌ No persistent storage
- ❌ Limited error handling
- ❌ No way to delete keys
- ❌ No help documentation
- ❌ Keys lost on restart

---

## Migration Guide (1.0 to 2.0)

### For Users
1. All stored keys from v1.0 will be lost (in-memory storage)
2. Simply re-add your keys after upgrading
3. Keys will now persist across restarts

### For Developers/Deployers
1. **IMPORTANT**: Remove any hardcoded credentials
2. Set environment variables:
   ```bash
   export API_ID='your-api-id'
   export API_HASH='your-api-hash'
   export BOT_TOKEN='your-bot-token'
   ```
3. Update dependencies:
   ```bash
   pip3 install -r requirements.txt --upgrade
   ```
4. Restart the bot
5. Check logs for successful startup

### Breaking Changes
- API_ID, API_HASH, BOT_TOKEN **must** be set as environment variables
- No default values provided (will raise ValueError if not set)
- Session file name changed (old session can be deleted)

---

## Future Roadmap

### Planned Features
- [ ] Database support (PostgreSQL/MongoDB)
- [ ] Multiple 2FA keys per user
- [ ] Key nicknames/labels
- [ ] Export/Import functionality
- [ ] Admin panel
- [ ] Usage statistics
- [ ] Scheduled key rotation reminders
- [ ] QR code scanning support
- [ ] Multi-language support

### Under Consideration
- [ ] Web interface
- [ ] Backup codes storage
- [ ] Two-factor recovery options
- [ ] Integration with password managers
- [ ] Audit logs
- [ ] Rate limiting per user

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/DAXXTEAM/2FA/issues
- Telegram: https://t.me/vlubtech

---

**Note**: This project follows [Semantic Versioning](https://semver.org/).
