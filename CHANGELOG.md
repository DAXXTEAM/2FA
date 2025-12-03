# Changelog

All notable changes to this project will be documented in this file.

## [2.0.0] - 2025-12-03

### 🔒 Security
- **CRITICAL**: Removed hardcoded credentials from source code
- Added automatic message deletion for 2FA keys
- Implemented proper environment variable validation
- Added security warnings and best practices documentation
- Created `.gitignore` to prevent credential leaks

### ✨ Added
- Comprehensive logging system with timestamps
- `/help` command with detailed usage instructions
- Real-time TOTP code validity display (shows remaining seconds)
- Improved error messages with detailed guidance
- Session file patterns to `.gitignore`
- `.env.example` template for easy configuration
- `LICENSE` file (MIT License)
- `runtime.txt` for Heroku Python version specification
- `SECURITY.md` with security guidelines
- Extensive README documentation
- Key length validation (minimum 16 characters)
- Better Base32 format validation
- FloodWait exception handling
- Graceful shutdown handling

### 🔄 Changed
- Removed unused `bot` Client instance (only using `app`)
- Updated requirements.txt with specific version numbers:
  - pyrogram==2.0.106
  - tgcrypto==1.2.5
  - pyotp==2.9.0
- Rewrote main function to use async/await properly
- Enhanced app.json with better descriptions and metadata
- Improved button cooldown feedback messages
- Updated all callback handlers with try-except blocks
- Added username logging for better monitoring
- Enhanced "About Bot" section with more details

### 🐛 Fixed
- Fixed potential security vulnerability with hardcoded credentials
- Fixed missing error handling in callback queries
- Fixed improper exception handling
- Added missing imports (asyncio, Optional)
- Fixed message filter to exclude commands from key handler

### 📝 Documentation
- Complete rewrite of README.md with:
  - Detailed deployment guides for Heroku and VPS
  - Prerequisites section
  - Usage instructions for end users
  - Security best practices
  - Troubleshooting guide
  - Development setup guide
  - Configuration options
  - Project structure
- Added inline code documentation
- Created comprehensive .env.example

### 🎨 Improvements
- Better code organization and structure
- Consistent error message formatting
- Enhanced user feedback messages
- Improved keyboard layout descriptions
- Better logging format and information
- Professional startup banner in logs

## [1.0.0] - Initial Release

### Added
- Basic 2FA bot functionality
- TOTP code generation
- Button cooldown system
- In-memory key storage
