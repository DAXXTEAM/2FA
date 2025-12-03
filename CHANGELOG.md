# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-03

### Added
- **Enhanced Security**
  - Removed hardcoded credentials from source code
  - Added comprehensive logging system
  - Improved input validation for 2FA keys
  - Added key length validation (minimum 16 characters)
  - Automatic removal of spaces and hyphens from input keys

- **New Commands**
  - `/help` - Display detailed help and usage instructions
  - `/remove` - Remove stored 2FA key from memory

- **User Experience Improvements**
  - Added code expiry timer (shows remaining validity time)
  - Better error messages with actionable guidance
  - Enhanced keyboard layouts with better organization
  - Added privacy notices about key storage

- **Code Quality**
  - Comprehensive error handling with try-catch blocks
  - Proper async/await patterns with FloodWait handling
  - Type hints for better code clarity
  - Removed duplicate client instance
  - Better code organization and comments

- **Documentation**
  - Complete README rewrite with detailed instructions
  - Added CONTRIBUTING.md for contributors
  - Added CHANGELOG.md for version tracking
  - Added LICENSE file (MIT)
  - Added .env.example template
  - Added comprehensive .gitignore

- **Dependencies**
  - Added TgCrypto for better performance
  - Pinned dependency versions for stability
  - Updated to Pyrogram 2.0+

### Changed
- Improved button cooldown system with better user feedback
- Enhanced TOTP code display with validity timer
- Better session file naming
- Improved about page with more information

### Fixed
- Security vulnerability with exposed credentials
- Duplicate Pyrogram client instances
- Missing error handling in multiple functions
- Incorrect filter on text message handler

### Security
- **CRITICAL**: Removed hardcoded API credentials
- Keys now properly validated and sanitized
- Session files added to .gitignore
- Environment variable validation

## [1.0.0] - Initial Release

### Added
- Basic 2FA key storage
- TOTP code generation
- Button cooldown system
- Base32 validation
- Inline keyboard interface
- Heroku deployment support
