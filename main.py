# @termux_superbot
# my telegram id: 2031050089


import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram import Update

debug_mode = True


load_dotenv()

"""
Пример .env файла:
BOT_TOKEN=TOKEN
SUPERUSER_ID=123456789
"""

BOT_TOKEN = os.getenv("BOT_TOKEN")
SUPERUSER_ID = int(os.getenv("SUPERUSER_ID", "0"))

if not BOT_TOKEN:
    print("[ERROR] BOT_TOKEN not found in environment variables!")
    exit(1)
if SUPERUSER_ID == 0:
    print("[ERROR] OWNER_USER_ID not found or invalid in environment variables!")
    exit(1)
    
bot_running = True
application = None
polling_task = None

async def send_message(text):
    """Sends a message to the superuser"""
    bot = Bot(token=BOT_TOKEN)
    try:
        await bot.send_message(
            chat_id=SUPERUSER_ID,
            text=text
        )
        
    except TelegramError as e:
        print(f"[ERROR] {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    superuser_msg = False
    """Handle incoming messages from users"""
    if update.message and update.message.text:
        user_id = update.message.from_user.id
        if user_id == SUPERUSER_ID:
            superuser_msg = True
        username = update.message.from_user.username or "unknown"
        first_name = update.message.from_user.first_name or ""
        text = update.message.text
        if superuser_msg == True:
            print(f"[MESSAGE] @{username} (superuser) (ID: {user_id}, {first_name}): {text}")
        else:
            print(f"[MESSAGE] @{username} (ID: {user_id}, {first_name}): {text}")

async def input_handler(application):
    """Phase input command handler"""
    global bot_running, polling_task
    
    loop = asyncio.get_event_loop()
    
    while bot_running:
        try:
            user_input = await loop.run_in_executor(None, input, "> ")
            user_input = user_input.strip()
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower() if parts else ""
            args = parts[1] if len(parts) > 1 else ""
            
            if command == "exit":
                bot_running = False
                await send_message("Бот завершает работу. 👋")
                if debug_mode:
                    print(f"[DEBUG] Exit message sent to superuser")
                print("Stopping bot...")
                await application.updater.stop()
                break
            
            elif command == "status":
                print("Bot alive")
            
            elif command == "send":
                if not args:
                    print("Usage: send [ID] [text]")
                else:
                    parts_send = args.split(maxsplit=1)
                    if len(parts_send) < 2:
                        print("Usage: send [ID] [text]")
                    else:
                        user_id = parts_send[0]
                        message = parts_send[1]
                        try:
                            bot = Bot(token=BOT_TOKEN)
                            if user_id == "superuser":
                                user_id = SUPERUSER_ID
                            await bot.send_message(chat_id=int(user_id), text=message)
                            print("Message sent successfully")
                        except ValueError:
                            print("[ERROR] Invalid user ID format")
                        except TelegramError as e:
                            print(f"[ERROR] {e}")
            
            elif command == "help":
                print("""
Available commands:
    exit              - turn off the bot
    status            - status of the bot
    send [ID] [MSG]   - send message to user with specified id
    help              - show this help message
                """)
            
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        
        except Exception as e:
            print(f"[ERROR] {e}")

async def main():
    global bot_running, application, polling_task
    
    await send_message("Бот онлайн! 🚀")
        
    if debug_mode:
            print(f"[DEBUG] Hello message sent to superuser")
    
    print("╔════════════════════════════════════╗")
    print("║          TERMUX - CONSOLE          ║")
    print("╚════════════════════════════════════╝")
    print("\nFor command list type help\n")
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    async with application:
        await application.start()
        polling_task = asyncio.create_task(application.updater.start_polling())
        await input_handler(application)
        await application.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] {e}")