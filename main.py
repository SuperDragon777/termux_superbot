import asyncio
import os
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from telegram import Update
from datetime import datetime

debug_mode = True
version = "1.5"
MAX_MESSAGE_SIZE = 512

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
bot_start_time = None
messages_received = 0

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
    finally:
        await bot.close()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global messages_received
    """Handle incoming messages from users"""
    if update.message and update.message.text:
        messages_received += 1
        user_id = update.message.from_user.id
        superuser_msg = user_id == SUPERUSER_ID
        username = update.message.from_user.username or "unknown"
        first_name = update.message.from_user.first_name or ""
        text = update.message.text
        if superuser_msg:
            print(f"[MESSAGE] @{username} (superuser) (ID: {user_id}, {first_name}): {text}")
        else:
            print(f"[MESSAGE] @{username} (ID: {user_id}, {first_name}): {text}")

def calculate_uptime():
    """Calculate uptime correctly"""
    global bot_start_time
    uptime = datetime.now() - bot_start_time
    days = uptime.days
    hours = (uptime.seconds // 3600)
    minutes = (uptime.seconds % 3600) // 60
    seconds = uptime.seconds % 60
    return days, hours, minutes, seconds

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command from any user"""
    global bot_start_time
    
    if bot_running:
        days, hours, minutes, seconds = calculate_uptime()
        
        status_text = f"🤖 Status: Online\nUptime: {days}d {hours}h {minutes}m {seconds}s\nVersion: {version}\n\nBot alive! 🚀"
    else:
        status_text = "Something went wrong. ❌"
    
    await update.message.reply_text(status_text)
    
    if debug_mode:
        print(f"[DEBUG] Status command used by user {update.message.from_user.id}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stop command from superuser"""
    global bot_running
    
    user_id = update.message.from_user.id
    
    if user_id != SUPERUSER_ID:
        await update.message.reply_text("No permission. ❌")
        print(f"[WARNING] Unauthorized /stop command attempt by user ID: {user_id}")
        return
    
    await update.message.reply_text("Bot shutting down. 👋")
    print(f"[INFO] Bot shutdown initiated by superuser")
    print("Stopping bot...")
    bot_running = False
    await application.stop()

def print_console_status():
    """Print detailed bot status in console"""
    global bot_start_time, messages_received
    
    days, hours, minutes, seconds = calculate_uptime()
    
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    debug_str = "ON" if debug_mode else "OFF"
    status_str = "Online ✅"
    
    print("\nBot Status:")
    print(f"Status:                 {status_str}")
    print(f"Version:                {version}")
    print(f"Uptime:                 {uptime_str}")
    print(f"Messages Received:      {str(messages_received)}")
    print(f"Superuser ID:           {str(SUPERUSER_ID)}")
    print(f"Debug Mode:             {debug_str}\n")

def truncate_message(text, max_size=MAX_MESSAGE_SIZE):
    """Truncate message if it exceeds max size"""
    if len(text.encode('utf-8')) > max_size:
        text = text[:max_size-3] + "..."
    return text

async def input_handler(application):
    """Phase input command handler"""
    global bot_running
    
    loop = asyncio.get_event_loop()
    
    while bot_running:
        try:
            user_input = await asyncio.wait_for(
                loop.run_in_executor(None, input, "> "),
                timeout=1.0
            )
            user_input = user_input.strip()
            
            parts = user_input.split(maxsplit=1)
            command = parts[0].lower() if parts else ""
            args = parts[1] if len(parts) > 1 else ""
            
            if command == "exit":
                bot_running = False
                await send_message("Bot shutting down. 👋")
                if debug_mode:
                    print(f"[DEBUG] Exit message sent to superuser")
                print("Stopping bot...")
                await application.stop()
                break
            
            elif command == "status":
                print_console_status()
            
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
                            
                            message = truncate_message(message)
                            
                            await bot.send_message(chat_id=int(user_id), text=message)
                            print("Message sent successfully")
                            await bot.close()
                        except ValueError:
                            print("[ERROR] Invalid user ID format")
                        except TelegramError as e:
                            print(f"[ERROR] {e}")
            
            elif command == "help":
                print("""
Available commands:
    exit              - turn off the bot
    status            - status of the bot
    send [ID] [MSG]   - send message to user
    help              - show this help message
                """)
            
            else:
                print("Unknown command. Type 'help' for a list of commands.")
        
        except asyncio.TimeoutError:
            continue
        except Exception as e:
            print(f"[ERROR] {e}")

async def main():
    global bot_running, application, bot_start_time
    
    bot_start_time = datetime.now()
    
    await send_message("Bot online! 🚀")
        
    if debug_mode:
            print(f"[DEBUG] Hello message sent to superuser")
    
    print("╔════════════════════════════════════╗")
    print("║          TERMUX - CONSOLE          ║")
    print("╚════════════════════════════════════╝")
    print("\nFor command list type help\n")
    
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("stop", stop_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    async with application:
        await application.start()
        await input_handler(application)
        await application.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] {e}")