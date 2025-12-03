# Contributing to 2FA Manager Bot

First off, thank you for considering contributing to this project! 🎉

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

- **Use a clear and descriptive title**
- **Describe the exact steps to reproduce the problem**
- **Provide specific examples**
- **Describe the behavior you observed and what you expected**
- **Include screenshots if applicable**
- **Include your environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion:

- **Use a clear and descriptive title**
- **Provide a detailed description of the suggested enhancement**
- **Explain why this enhancement would be useful**
- **List some examples of how it would be used**

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following the code style guidelines
3. **Test your changes** thoroughly
4. **Update documentation** if needed
5. **Commit your changes** with clear commit messages
6. **Push to your fork** and submit a pull request

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/2FA.git
cd 2FA
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your test bot credentials
```

5. Run the bot:
```bash
python3 2FA.py
```

## Code Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions small and focused on a single task
- Add comments for complex logic
- Use type hints where applicable

## Commit Message Guidelines

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

Examples:
```
Add /stats command for user statistics
Fix TOTP generation for keys with padding
Update README with Docker deployment guide
```

## Testing

- Test your changes with different scenarios
- Test error handling and edge cases
- Verify that existing functionality still works
- Test on different platforms if possible

## Security

- **Never commit sensitive data** (tokens, API keys, passwords)
- **Review security implications** of your changes
- **Report security vulnerabilities** privately to the maintainers

## Questions?

Feel free to:
- Open an issue for discussion
- Join our [Telegram support group](https://t.me/vlubtech)
- Contact the maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for your contribution! 🙏
