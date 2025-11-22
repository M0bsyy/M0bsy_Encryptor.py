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
    welcome_message = """🔐 **File Encryption Bot**

Welcome! I can encrypt and decrypt your files using XOR encryption.

**How to use:**
- `/encrypt password` - Set encryption mode with password
- `/decrypt password` - Set decryption mode with password
- Then send the file

**Commands:**
- `/start` - Show this message
- `/help` - Get help

⚠️ Remember your password! Without it, you cannot decrypt."""
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler."""
    help_text = """📖 **Help**

**Encryption Process:**
1. Send: `/encrypt mypassword`
2. Send the file to encrypt
3. Receive encrypted file

**Decryption Process:**
1. Send: `/decrypt mypassword`
2. Send the encrypted file
3. Receive original file

**Important:**
- Use same password for encrypt and decrypt
- Passwords are case-sensitive
- Bot deletes files after processing"""
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
    
    await update.message.reply_text(f"✅ Ready to encrypt\n\n📤 Send the file to encrypt", parse_mode='Markdown')


async def set_decrypt_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set decryption mode and password."""
    if len(context.args) == 0:
        await update.message.reply_text("❌ Usage: `/decrypt password`", parse_mode='Markdown')
        return
    
    password = ' '.join(context.args)
    context.user_data['mode'] = 'decrypt'
    context.user_data['password'] = password
    context.user_data['file_waiting'] = True
    
    await update.message.reply_text(f"✅ Ready to decrypt\n\n📤 Send the file to decrypt", parse_mode='Markdown')


async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle file uploads for encryption/decryption."""
    
    if not context.user_data.get('file_waiting'):
        await update.message.reply_text("❌ Please set mode first\n\nUse:\n`/encrypt password`\n`/decrypt password`", parse_mode='Markdown')
        return
    
    if update.message.document is None:
        await update.message.reply_text("❌ Please send a file")
        return
    
    mode = context.user_data.get('mode')
    password = context.user_data.get('password')
    
    if not mode or not password:
        await update.message.reply_text("❌ Error: Mode or password not set")
        return
    
    temp_dir = None
    try:
        temp_dir = tempfile.mkdtemp()
        
        file_obj = await context.bot.get_file(update.message.document.file_id)
        input_path = os.path.join(temp_dir, update.message.document.file_name or "file")
        await file_obj.download_to_drive(input_path)
        
        if mode == 'encrypt':
            output_name = f"{update.message.document.file_name or 'file'}.encrypted"
            output_path = os.path.join(temp_dir, output_name)
            success = encrypt_file(input_path, output_path, password)
            message = "🔐 File encrypted successfully!"
        else:
            output_name = update.message.document.file_name or "file"
            if output_name.endswith('.encrypted'):
                output_name = output_name[:-10]
            output_path = os.path.join(temp_dir, output_name)
            success = decrypt_file(input_path, output_path, password)
            message = "🔓 File decrypted successfully!"
        
        if not success:
            await update.message.reply_text("❌ Failed to process file")
            return
        
        await update.message.reply_text(message)
        
        with open(output_path, 'rb') as f:
            await context.bot.send_document(
                chat_id=update.message.chat_id,
                document=f,
                filename=output_name,
                caption=f"✅ {'Encrypted' if mode == 'encrypt' else 'Decrypted'}"
            )
        
        context.user_data.pop('mode', None)
        context.user_data.pop('password', None)
        context.user_data.pop('file_waiting', None)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text(f"❌ Error: {str(e)[:100]}")
    
    finally:
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except:
                pass


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle general messages."""
    await update.message.reply_text("❌ Please send a file\n\nUse:\n`/encrypt password`\n`/decrypt password`\n`/help`", parse_mode='Markdown')


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
