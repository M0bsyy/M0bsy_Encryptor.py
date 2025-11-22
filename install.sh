#!/bin/bash

# Telegram File Encryption Bot - Installation Script

echo "================================================"
echo "🔐 Telegram File Encryption Bot - Installer"
echo "================================================"
echo ""

# Check Python version
echo "[1/3] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    echo "Install Python 3.8+ from https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo "✓ Python $PYTHON_VERSION found"
echo ""

# Install dependencies
echo "[2/3] Installing dependencies..."
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi

pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi
echo ""

# Create temp directory if needed
echo "[3/3] Creating directories..."
mkdir -p temp
echo "✓ Directories ready"
echo ""

# Final instructions
echo "================================================"
echo "✅ Installation Complete!"
echo "================================================"
echo ""
echo "NEXT STEPS:"
echo "1. Get your Telegram bot token from @BotFather"
echo "2. Set your token as environment variable:"
echo "   export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
echo "3. Run the verify script:"
echo "   bash verify.sh"
echo "4. Start the bot:"
echo "   python bot.py"
echo ""
echo "Need help? Read README.md"
echo ""
