import os
import requests
import logging
from telegram import Update, ForceReply
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from functools import wraps
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 챗GPT API 키
GPT_API_KEY = os.getenv('GPT_API_KEY')
# 텔레그램 봇 토큰
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
# 텔레그램 사용자 ID (인증용)
USER_ID = int(os.getenv('TELEGRAM_USER_ID', 0))

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create the Application and pass it your bot's token.
application = Application.builder().token(TELEGRAM_TOKEN).build()

def get_gpt_response(prompt, api_key):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': 'gpt-3.5-turbo',  # 모델명
        'messages': [{"role": "user", "content": prompt}],  # 대화 형식
        'max_tokens': 150
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    return response.json()['choices'][0]['message']['content'].strip()

def auth(user_id):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            if update.effective_user.id == user_id:
                await func(update, context)
            else:
                await update.message.reply_text("You are not authorized to use this bot")
        return wrapper
    return decorator

@auth(USER_ID)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

@auth(USER_ID)
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")

@auth(USER_ID)
async def reload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /reload is issued."""
    await update.message.reply_text("Reloaded the bot!")

@auth(USER_ID)
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    user_message = update.message.text
    response = get_gpt_response(user_message, GPT_API_KEY)
    await update.message.reply_text(response)

def main():
    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reload", reload))
    
    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
