import os
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

# Read the variable from the environment (or .env file)
bot_token = os.getenv('BOT_TOKEN')
secret_token = os.getenv("SECRET_TOKEN")
webhook_url = os.getenv('CYCLIC_URL', 'http://localhost:8181') + "/webhook/"

bot = Bot(token=bot_token)
# bot.set_webhook(url=webhook_url)
# webhook_info = bot.get_webhook_info()
# print(webhook_info)

ptb = (
    Application.builder()
    .token(secret_token)
    .read_timeout(7)
    .get_updates_read_timeout(42)
    .updater(None)
)
# if config.ENV:
#     ptb = ptb.updater(None)
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

@app.get("/")
def home():
    return "Hello world!"


async def error(update, context: ContextTypes.DEFAULT_TYPE):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

# custom messages
start_message = "<b>Ready to get fit?!</b>\n\nTo start, you can use following commands."  # html

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # with open('hello.gif', 'rb') as photo:
    #     await update.message.reply_photo(photo=photo)
    await update.message.reply_text(
        reply_markup=ForceReply(selective=True),
        text=start_message,
        parse_mode=ParseMode.HTML,
    )

def add_handlers(dp):
    # conversations (must be declared first, not sure why)
    # dp.add_handler(convo_handlers.edit_handler)
    # dp.add_handler(convo_handlers.config_chat_handler)

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    # dp.add_handler(CommandHandler("help", commands.help))
    # dp.add_handler(CommandHandler("add", commands.add))
    # dp.add_handler(CommandHandler("delete", commands.delete))
    # dp.add_handler(CommandHandler("list", commands.list_jobs))
    # dp.add_handler(CommandHandler("checkcron", commands.checkcron))
    # dp.add_handler(CommandHandler("options", commands.list_options))
    # dp.add_handler(CommandHandler("adminsonly", commands.option_restrict_to_admins))
    # dp.add_handler(CommandHandler("creatoronly", commands.option_restrict_to_user))
    # dp.add_handler(CommandHandler("changetz", commands.change_tz))
    # dp.add_handler(CommandHandler("reset", commands.reset))
    # dp.add_handler(CommandHandler("addmultiple", commands.add_multiple))

    # on noncommand i.e message
    # dp.add_handler(MessageHandler(filters.TEXT, handlers.handle_messages))
    # dp.add_handler(MessageHandler(filters.PHOTO, handlers.handle_photos))
    # dp.add_handler(MessageHandler(filters.POLL, handlers.handle_polls))

    # # on callback
    # dp.add_handler(CallbackQueryHandler(handlers.handle_callback))

    # log all errors
    dp.add_error_handler(error)


add_handlers(ptb)

# Use webhook when running in prod (via gunicorn)
# if config.ENV:

@app.post("/webhook/")
async def process_update(request: Request):
    req = await request.json()
    update = Update.de_json(req, ptb.bot)
    await ptb.process_update(update)
    return Response(status_code=HTTPStatus.OK)



# def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
#     # return true # uncomment to disable authentication
#     if x_telegram_bot_api_secret_token != secret_token:
#         raise HTTPException(status_code=403, detail="Not authenticated")
#     return x_telegram_bot_api_secret_token

# @app.post("/webhook/")
# async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
#     chat_id = update.message["chat"]["id"]
#     text = update.message["text"]
#     print("Received message:", update.message)

#     if text == "/start":
#         with open('hello.gif', 'rb') as photo:
#             await bot.send_photo(chat_id=chat_id, photo=photo)
#         await bot.send_message(chat_id=chat_id, text="Welcome to Cyclic Starter Python Telegram Bot!")
#     else:
#         await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Yo!")

#     return {"ok": True}