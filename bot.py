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
# 텔레그램 봇 사용자 이름
BOT_USERNAME = "@GunnerHughBot"

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

def auth(bot_username):
    def decorator(func):
        @wraps(func)
        async def wrapper(update, context):
            if update.effective_user.username == bot_username:
                await func(update, context)
            else:
                await update.message.reply_text("You are not authorized to use this bot")
        return wrapper
    return decorator

@auth(BOT_USERNAME)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

@auth(BOT_USERNAME)
​⬤
