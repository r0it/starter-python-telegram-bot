import os, stat
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
start_message = "<b>Ready to get fit?</b>\n\nTrying fooling around with following commands. \n\n/trackMyCal (to track calories detail from your food image) \n\n/ama (Ask Me Anything)"  # html
convo_end_msg = "Enjoying??? \n\n/trackMyCal (to track calories detail from your food image) \n\n/ama (Ask Me Anything)"

PHOTO = range(0)
PROMPT = range(0)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text=start_message,
        parse_mode=ParseMode.HTML
    )

async def initiate_ama(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ask me anything. Eg. Write a 50 words essay on A.I. \n\n/cancel to cancel the operation")
    return PROMPT

async def track_my_cal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Upload an image of your food to track calories. \n\n/cancel to cancel the operation")
    return PHOTO

async def end_convo(update, _: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        text = 'To track more food dishes, \n\n/trackMyCal (to track calories detail from your food image) \n\n/ama (Ask Me Anything)"',
        parse_mode=ParseMode.HTML)  # html
    return ConversationHandler.END


async def analyze_food_dish(update, _: ContextTypes.DEFAULT_TYPE):
    logger.info("trackCal by: %s", update.message.chat.first_name)
    food_photo = await update.message.photo[-1].get_file()
    file_name='food_photo.jpg'
    # os.chmod('uploads', stat.S_IWRITE)
    await food_photo.download_to_drive(file_name)
    genResponse = genai.response(file_name, config.TRACK_FOOD_PROMPT)
    await update.message.reply_text(
        text = genResponse + "\n\n------\n\n" + convo_end_msg,
        parse_mode=ParseMode.HTML)  # html
    return ConversationHandler.END


async def ask_me_anything(update, _: ContextTypes.DEFAULT_TYPE):
    logger.info("ama by: %s", update.message.chat.first_name)
    genResponse = genai.response(None, update.message.text)
    await update.message.reply_text(
        text = genResponse + "\n\n------\n\n" + convo_end_msg,
        parse_mode=ParseMode.HTML)  # html
    return ConversationHandler.END

convo_text_filter = filters.TEXT & ~filters.COMMAND

track_my_cal_convo_handler = ConversationHandler(
    entry_points=[CommandHandler("trackMyCal", track_my_cal)],
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
