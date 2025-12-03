# Contributing to 2FA Bot

Thank you for your interest in contributing to the 2FA Telegram Bot! This document provides guidelines and instructions for contributing.

## 🌟 Ways to Contribute

- 🐛 Report bugs
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit code fixes
- 🎨 Enhance UI/UX
- 🌍 Add translations
- 🧪 Write tests

## 🚀 Getting Started

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR_USERNAME/2FA.git
cd 2FA
```

### 2. Set Up Development Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your test credentials
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/changes

## 📝 Code Guidelines

### Python Style

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions small and focused
- Use type hints where appropriate

### Code Example

```python
async def example_function(user_id: int, message: str) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        user_id: The Telegram user ID
        message: The message text to process
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Implementation
        logger.info(f"Processing message for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error in example_function: {e}", exc_info=True)
        return False
```

### Logging

Always include appropriate logging:

```python
# Info level for normal operations
logger.info(f"User {user_id} performed action")

# Warning for recoverable issues
logger.warning(f"Rate limit hit for user {user_id}")

# Error for exceptions
logger.error(f"Failed to process: {e}", exc_info=True)
```

### Error Handling

Always use proper error handling:

```python
try:
    # Your code
    pass
except SpecificException as e:
    logger.error(f"Specific error: {e}")
    # Handle specifically
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    # Generic handling
```

## 🧪 Testing

Before submitting:

1. **Test your changes locally**
   ```bash
   python3 2FA.py
   ```

2. **Check for syntax errors**
   ```bash
   python3 -m py_compile 2FA.py
   ```

3. **Test all bot commands**
   - `/start`
   - `/help`
   - All callback buttons
   - 2FA key submission
   - TOTP generation

4. **Test edge cases**
   - Invalid keys
   - Empty inputs
   - Special characters
   - Very long inputs

## 📋 Commit Guidelines

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

### Examples

```bash
feat: add multi-language support

- Added English and Spanish translations
- Implemented language selection menu
- Updated documentation

Closes #123
```

```bash
fix: resolve cooldown timer issue

The cooldown timer was not resetting properly after 30 seconds.
Fixed by improving the time calculation logic.

Fixes #456
```

## 🔍 Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Check your changes**
   ```bash
   git status
   git diff
   ```

3. **Commit your changes**
   ```bash
   git add .
   git commit -m "type: description"
   ```

4. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting PR

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your branch
4. Fill in the PR template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
How did you test these changes?

## Screenshots (if applicable)
Add screenshots here

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
- [ ] Tested locally
```

### PR Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, PR will be merged
4. Your contribution will be credited!

## 🐛 Bug Reports

### Before Submitting

1. Check if bug already reported
2. Test with latest version
3. Gather relevant information

### Bug Report Template

```markdown
**Describe the Bug**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Enter '...'
4. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Screenshots**
If applicable

**Environment**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.7]
- Bot Version: [e.g., 2.0.0]
- Deployment: [e.g., Heroku, VPS]

**Logs**
Relevant log output

**Additional Context**
Any other information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired solution

**Describe alternatives you've considered**
Other solutions you've thought about

**Additional context**
Mockups, examples, etc.
```

## 📚 Documentation

### Documentation Updates

- Keep README.md up to date
- Update CHANGELOG.md
- Add inline code comments
- Update type hints
- Create examples for new features

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots when helpful
- Keep formatting consistent
- Test all commands/examples

## 🔐 Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities.

Instead:
1. Email or contact privately (see SECURITY.md)
2. Provide detailed description
3. Include reproduction steps
4. Suggest fix if possible

### Security Guidelines

- Never commit credentials
- Use environment variables
- Validate all inputs
- Handle errors properly
- Keep dependencies updated
- Follow OWASP guidelines

## 🎨 Code Review Checklist

Reviewers will check:

- [ ] Code follows Python style guidelines
- [ ] All functions have docstrings
- [ ] Error handling is present
- [ ] Logging is appropriate
- [ ] No hardcoded credentials
- [ ] No security vulnerabilities
- [ ] Documentation is updated
- [ ] Code is well-tested
- [ ] Commit messages are clear
- [ ] No unnecessary changes

## 📞 Getting Help

Need help? Here's where to ask:

- **General Questions**: [Telegram Support](https://t.me/vlubtech)
- **Bug Reports**: [GitHub Issues](https://github.com/DAXXTEAM/2FA/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/DAXXTEAM/2FA/discussions)

## 🏆 Recognition

Contributors will be:
- Listed in CHANGELOG.md
- Credited in release notes
- Acknowledged in README.md (for significant contributions)

## 📜 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone.

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what's best for the community
- Showing empathy towards others

**Unacceptable behaviors:**
- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

### Enforcement

Report violations to project maintainers. All reports will be reviewed and investigated.

## 🙏 Thank You!

Thank you for contributing to the 2FA Bot project! Your contributions help make this project better for everyone.

---

**Questions?** Don't hesitate to ask! We're here to help. 😊
