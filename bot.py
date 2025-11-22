"""Telegram bot for XOR file encryption."""

import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from encryption import encrypt_file, decrypt_file
import tempfile
import shutil

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    welcome_message = """
🔐 **File Encryption Bot**

Welcome! I can encrypt and decrypt your files using XOR encryption.

**How to use:**
1. Send me a file with password: `/encrypt password`
2. Reply to the encrypted file with: `/decrypt password`

**Commands:**
- `/start` - Show this message
- `/help` - Get help
- `/encrypt password` - Encrypt the next file you send
- `/decrypt password` - Decrypt the next file you send

**Example:**
1. Send file → type `/encrypt mypassword`
2. I'll encrypt and send it back
3. To decrypt: Send encrypted file → type `/decrypt mypassword`

⚠️ Remember your password! Without it, you cannot decrypt.
"""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler."""
    help_text = """
📖 **Help**

**What this bot does:**
- Encrypts files using XOR encryption + compression
- Decrypts encrypted files
- Works with any file type

**How to encrypt:**
1. Send the command: `/encrypt yourpassword`
2. Send the file you want to encrypt
3. I'll encrypt it and send it back

**How to decrypt:**
1. Send the command: `/decrypt yourpassword`
2. Send the encrypted file
3. I'll decrypt it and send it back

**Important:**
- Store your passwords safely
- The encryption/decryption is done securely
- Encrypted files are temporary

**Example workflow:**
- You: `/encrypt secret123`
- You: [send file.txt]
- Bot: [sends encrypted file.txt.encrypted]
- You: `/decrypt secret123`
- You: [send file.txt.encrypted]
- Bot: [sends decrypted file.txt]
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def set_encrypt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set encryption mode and password."""
    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: `/encrypt password`", parse_mode='Markdown')
        return
    
    password = ' '.join(context.args)
    context.user_data['mode'] = 'encrypt'
    context.user_data['password'] = password
    context.user_data['file_waiting'] = True
    
    await update.message.reply_text(
        f"✅ Encryption mode enabled\nPassword set\n\n📤 Send the file you want to encrypt",
        parse_mode='Markdown'
    )

async def set_decrypt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set decryption mode and password."""
    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: `/decrypt password`", parse_mode='Markdown')
        return
    
    password = ' '.join(context.args)
    context.user_data['mode'] = 'decrypt'
    context.user_data['password'] = password
    context.user_data['file_waiting'] = True
    
    await update.message.reply_text(
        f"✅ Decryption mode enabled\nPassword set\n\n📤 Send the file you want to decrypt",
        parse_mode='Markdown'
    )

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads for encryption/decryption."""
    
    if not context.user_data.get('file_waiting'):
        await update.message.reply_text(
            "❌ Please set mode first\n\nUse:\n`/encrypt password` - to encrypt\n`/decrypt password` - to decrypt",
            parse_mode='Markdown'
        )
        return
    
    if update.message.document is None:
        await update.message.reply_text("❌ Please send a file")
        return
    
    mode = context.user_data.get('mode')
    password = context.user_data.get('password')
    
    if not mode or not password:
        await update.message.reply_text("❌ Error: Mode or password not set")
        return
    
    try:
        temp_dir = tempfile.mkdtemp()
        
        file_obj = await context.bot.get_file(update.message.document.file_id)
        input_path = os.path.join(temp_dir, update.message.document.file_name)
        await file_obj.download_to_drive(input_path)
        
        if mode == 'encrypt':
            output_name = f"{update.message.document.file_name}.encrypted"
            output_path = os.path.join(temp_dir, output_name)
            encrypt_file(input_path, output_path, password)
            message = "🔐 File encrypted successfully!"
        else:
            output_name = update.message.document.file_name
            if output_name.endswith('.encrypted'):
                output_name = output_name[:-10]
            output_path = os.path.join(temp_dir, output_name)
            decrypt_file(input_path, output_path, password)
            message = "🔓 File decrypted successfully!"
        
        await update.message.reply_text(message)
        await context.bot.send_document(
            chat_id=update.message.chat_id,
            document=open(output_path, 'rb'),
            filename=output_name,
            caption=f"✅ {'Encrypted' if mode == 'encrypt' else 'Decrypted'} file"
        )
        
        shutil.rmtree(temp_dir)
        
        context.user_data.pop('mode', None)
        context.user_data.pop('password', None)
        context.user_data.pop('file_waiting', None)
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        error_msg = str(e)
        
        if "zlib" in error_msg.lower() or "decompress" in error_msg.lower():
            await update.message.reply_text(
                "❌ Decryption failed!\n\nPossible reasons:\n- Wrong password\n- File is not encrypted with this bot\n- File is corrupted",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(f"❌ Error: {error_msg}")
        
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general messages."""
    await update.message.reply_text(
        "❌ Please send a file or use commands:\n\n`/encrypt password` - Encrypt a file\n`/decrypt password` - Decrypt a file\n`/help` - Get help",
        parse_mode='Markdown'
    )

def main():
    """Start the bot."""
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("encrypt", set_encrypt_mode))
    application.add_handler(CommandHandler("decrypt", set_decrypt_mode))
    
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Starting bot...")
    application.run_polling()

if __name__ == '__main__':
    main()
