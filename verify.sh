#!/bin/bash

# Telegram File Encryption Bot - Verification Script

echo "================================================"
echo "🔍 Telegram File Encryption Bot - Verifier"
echo "================================================"
echo ""

ERRORS=0

# Check Python
echo "[1/5] Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    ERRORS=$((ERRORS+1))
else
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo "✓ Python $PYTHON_VERSION"
fi
echo ""

# Check environment variable
echo "[2/5] Checking TELEGRAM_BOT_TOKEN..."
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN not set"
    echo "   Run: export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    ERRORS=$((ERRORS+1))
else
    TOKEN_LENGTH=${#TELEGRAM_BOT_TOKEN}
    if [ $TOKEN_LENGTH -lt 30 ]; then
        echo "⚠️  Token looks too short (length: $TOKEN_LENGTH)"
    else
        echo "✓ TELEGRAM_BOT_TOKEN is set"
    fi
fi
echo ""

# Check files
echo "[3/5] Checking required files..."
REQUIRED_FILES=("bot.py" "encryption.py" "requirements.txt")
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "❌ $file not found"
        ERRORS=$((ERRORS+1))
    fi
done
echo ""

# Check dependencies
echo "[4/5] Checking Python dependencies..."
python3 -c "import telegram" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ python-telegram-bot installed"
else
    echo "❌ python-telegram-bot not installed"
    echo "   Run: bash install.sh"
    ERRORS=$((ERRORS+1))
fi
echo ""

# Import test
echo "[5/5] Testing imports..."
python3 -c "from encryption import encrypt_file, decrypt_file; print('✓ Encryption module OK')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ All imports successful"
else
    echo "❌ Import failed - check encryption.py"
    ERRORS=$((ERRORS+1))
fi
echo ""

# Final result
echo "================================================"
if [ $ERRORS -eq 0 ]; then
    echo "✅ All checks passed! You're ready to go."
    echo ""
    echo "Start the bot with:"
    echo "  python bot.py"
    exit 0
else
    echo "❌ $ERRORS check(s) failed"
    echo ""
    echo "Fix the issues and run verify.sh again"
    exit 1
fi
