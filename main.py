import os, stat
from util import escape_markdown_data
from datetime import datetime
import config
from gemini.gemini_vision import VisionAPI
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends, Request, Response
from telegram import Update, Bot, ForceReply
from telegram.constants import ParseMode
from pydantic import BaseModel
from contextlib import asynccontextmanager
from http import HTTPStatus
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
    CallbackQueryHandler,
    ContextTypes
)
import logging

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict

# Load variables from .env file if present
load_dotenv()

# Initialize the Gemini Vision API
genai = VisionAPI()
genai_user_requests = {} #  to limit requests before 60 seconds per user

# Read the variable from the environment (or .env file)
bot_token = config.TG_BOT_TOKEN
secret_token = config.TG_SECRET_TOKEN
webhook_url = config.CYCLIC_URL + "/webhook/"

bot = Bot(token=bot_token)
# bot.set_webhook(url=webhook_url)
# webhook_info = bot.get_webhook_info()
# print(webhook_info)

ptb = (
    Application.builder()
    .token(secret_token)
    .read_timeout(7)
    .get_updates_read_timeout(42)
)
if config.ENV:
    ptb = ptb.updater(None)

ptb = ptb.build()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if webhook_url:
        print(webhook_url)
        await ptb.bot.setWebhook(webhook_url)
    async with ptb:
        print('Bot Started')
        await ptb.start()
        yield
        await ptb.stop()


app = FastAPI(lifespan=lifespan) #FastAPI()

# Use webhook when running in prod (via gunicorn)
if config.ENV:
    @app.get("/")
    def home():
        return "Hello world!"


async def error(update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# custom messages
start_message = config.START_MSG

PHOTO = range(0)
PROMPT = range(0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text= escape_markdown_data(start_message),
        parse_mode=ParseMode.MARKDOWN_V2
    )


ama_txt = config.AMA_MSG

timeout_str = config.TIMEOUT_MSG

async def initiate_ama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id;
    time_now = datetime.now()
    # Allowing only 1 request per minute per user
    if (genai_user_requests.get(user_id) is None or
        (time_now - genai_user_requests.get(user_id)).total_seconds() > 60):
        genai_user_requests.update({user_id: time_now})
    else:
        await update.message.reply_text(
            text=escape_markdown_data(timeout_str),
            parse_mode=ParseMode.MARKDOWN_V2
            )
        return ConversationHandler.END
    await update.message.reply_text(
            text=escape_markdown_data(ama_txt),
            parse_mode=ParseMode.MARKDOWN_V2
            )
    return PROMPT

img_upload_txt = config.IMG_UPLOAD_MSG

async def track_my_cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id;
    time_now = datetime.now()
    # Allowing only 1 request per minute per user
    if (genai_user_requests.get(user_id) is None or
        (time_now - genai_user_requests.get(user_id)).total_seconds() > 60):
        genai_user_requests.update({user_id: time_now})
    else:
        await update.message.reply_text(
            text=escape_markdown_data(timeout_str),
            parse_mode=ParseMode.MARKDOWN_V2
            )
        return ConversationHandler.END
    await update.message.reply_text(
        text= escape_markdown_data(img_upload_txt),
        parse_mode=ParseMode.MARKDOWN_V2
        )
    return PHOTO

after_resp_sign = config.CONVO_END_MSG

async def end_convo(update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text = escape_markdown_data(after_resp_sign),
        parse_mode=ParseMode.MARKDOWN_V2)  # html
    return ConversationHandler.END


async def analyze_food_dish(update, _: ContextTypes.DEFAULT_TYPE):
    logger.info("trackCal by: %s", update.message.chat.first_name)
    food_photo = await update.message.photo[-1].get_file()
    imgBytes = await food_photo.download_as_bytearray()
    genResponse = genai.response(imgBytes, config.TRACK_FOOD_PROMPT)
    genResponse = genResponse + after_resp_sign
    genResponse = escape_markdown_data(genResponse)
    await update.message.reply_text(
        text = genResponse,
        parse_mode=ParseMode.MARKDOWN_V2) #HTML
    return ConversationHandler.END


async def ask_me_anything(update, _: ContextTypes.DEFAULT_TYPE):
    logger.info("ama by: %s", update.message.chat.first_name)
    genResponse = genai.response(None, update.message.text)
    genResponse = genResponse + after_resp_sign
    genResponse = escape_markdown_data(genResponse)
    await update.message.reply_text(
        text = genResponse,
        parse_mode=ParseMode.MARKDOWN_V2) #HTML
    return ConversationHandler.END

convo_text_filter = filters.TEXT & ~filters.COMMAND

track_my_cal_convo_handler = ConversationHandler(
    entry_points=[CommandHandler("scanMyImg", track_my_cal)],
    states={
        PHOTO: [
            MessageHandler(filters.PHOTO, analyze_food_dish)
        ]
    },
    fallbacks=[MessageHandler(filters.COMMAND, end_convo)],
)

ask_me_anything_convo_handler = ConversationHandler(
    entry_points=[CommandHandler("ama", initiate_ama)],
    states={
        PROMPT: [
            MessageHandler(convo_text_filter, ask_me_anything)
        ]
    },
    fallbacks=[MessageHandler(filters.COMMAND, end_convo)],
)

def add_handlers(dp):
    # conversations (must be declared first, not sure why)
    dp.add_handler(track_my_cal_convo_handler)
    dp.add_handler(ask_me_anything_convo_handler)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("ama", ask_me_anything))


    # log all errors
    dp.add_error_handler(error)


add_handlers(ptb)

# Use webhook when running in prod (via gunicorn)
if config.ENV:
    @app.post("/webhook/")
    async def process_update(request: Request):
        req = await request.json()
        update = Update.de_json(req, ptb.bot)
        await ptb.process_update(update)
        return Response(status_code=HTTPStatus.OK)
