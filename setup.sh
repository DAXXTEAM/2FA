#!/bin/bash
# Setup script for 2FA Telegram Bot

set -e

echo "=================================="
echo "2FA Bot Setup Script"
echo "=================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "Error: Python 3 is not installed!"
    exit 1
fi

# Check if pip is installed
echo ""
echo "Checking pip..."
pip3 --version

if [ $? -ne 0 ]; then
    echo "Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies!"
    exit 1
fi

echo ""
echo "=================================="
echo "Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Set up your environment variables:"
echo "   export API_ID='your-api-id'"
echo "   export API_HASH='your-api-hash'"
echo "   export BOT_TOKEN='your-bot-token'"
echo ""
echo "   OR copy .env.example to .env and edit it:"
echo "   cp .env.example .env"
echo "   nano .env"
echo "   source .env"
echo ""
echo "2. Run the bot:"
echo "   python3 2FA.py"
echo ""
echo "For detailed instructions, see README.md"
echo "=================================="
