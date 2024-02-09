import os
from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException, Depends, Response, Request
from telegram import Update, Bot
from pydantic import BaseModel
import asyncio
import html
import logging
from dataclasses import dataclass
from http import HTTPStatus
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackContext,
    CommandHandler,
    ContextTypes,
    ExtBot,
    TypeHandler,
)

class TelegramUpdate(BaseModel):
    update_id: int
    message: dict

@dataclass
class WebhookUpdate:
    """Simple dataclass to wrap a custom update type"""

    user_id: int
    payload: str


class CustomContext(CallbackContext[ExtBot, dict, dict, dict]):
    """
    Custom CallbackContext class that makes `user_data` available for updates of type
    `WebhookUpdate`.
    """

    @classmethod
    def from_update(
        cls,
        update: object,
        application: "Application",
    ) -> "CustomContext":
        if isinstance(update, WebhookUpdate):
            return cls(application=application, user_id=update.user_id)
        return super().from_update(update, application)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)

async def start(update: Update, context: CustomContext) -> None:
    """Display a message with instructions on how to use this bot."""
    # payload_url = html.escape(f"{URL}/submitpayload?user_id=<your user id>&payload=<payload>")
    # text = (
    #     f"To check if the bot is still running, call <code>{URL}/healthcheck</code>.\n\n"
    #     f"To post a custom update, call <code>{payload_url}</code>."
    # )
    # await update.message.reply_html(text=text)
    await update.message.reply_text('Hi, this is a test')

async def webhook_update(update: WebhookUpdate, context: CustomContext) -> None:
    """Handle custom updates."""
    # chat_member = await context.bot.get_chat_member(chat_id=update.user_id, user_id=update.user_id)
    # payloads = context.user_data.setdefault("payloads", [])
    # payloads.append(update.payload)
    # combined_payloads = "</code>\n• <code>".join(payloads)
    # text = (
    #     f"The user {chat_member.user.mention_html()} has sent a new payload. "
    #     f"So far they have sent the following payloads: \n\n• <code>{combined_payloads}</code>"
    # )
    # await context.bot.send_message(chat_id=update.user_id, text=text, parse_mode=ParseMode.HTML)
    await update.message.reply_text('Hi, this is a custom test')


# Load variables from .env file if present
load_dotenv()

# Read the variable from the environment (or .env file)
bot_token = os.getenv('BOT_TOKEN')
secret_token = os.getenv("SECRET_TOKEN")
webhook_url = os.getenv('CYCLIC_URL', 'http://localhost:8181') + "/webhook/"



app = FastAPI()

async def main() -> None:
    """Set up PTB application and a web application for handling the incoming requests."""
    context_types = ContextTypes(context=CustomContext)
    # Here we set updater to None because we want our custom webhook server to handle the updates
    # and hence we don't need an Updater instance
    application = (
        Application.builder().token(secret_token).updater(None).context_types(context_types).build()
    )

    # register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(TypeHandler(type=WebhookUpdate, callback=webhook_update))

    # Pass webhook settings to telegram
    await application.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)

    # Set up webserver
    app = FastAPI(__name__)
    
    @app.post("/webhook/")
    async def handle_webhook(request: Request) -> Response:
        """Handle incoming Telegram updates by putting them into the `update_queue`"""
        await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
        return Response(status=HTTPStatus.OK)


    async with application:
        await application.start()





# app = FastAPI()
# bot = Bot(token=bot_token)
# bot.set_webhook(url=webhook_url)
# webhook_info = bot.get_webhook_info()
# print(webhook_info)

# def auth_telegram_token(x_telegram_bot_api_secret_token: str = Header(None)) -> str:
#     # return true # uncomment to disable authentication
#     if x_telegram_bot_api_secret_token != secret_token:
#         raise HTTPException(status_code=403, detail="Not authenticated")
#     return x_telegram_bot_api_secret_token

# @app.get("/")
# async def hook():
#     print("Hello World")
    
# @app.post("/webhook/")
# async def handle_webhook(update: TelegramUpdate, token: str = Depends(auth_telegram_token)):
#     chat_id = await update.message["chat"]["id"]
#     text = update.message["text"]
#     print("Received message:", update.message)

#     if text == "/start":
#         with open('hello.gif', 'rb') as photo:
#             await bot.send_photo(chat_id=chat_id, photo=photo)
#         await bot.send_message(chat_id=chat_id, text="Welcome to Cyclic Starter Python Telegram Bot!")
#     else:
#         await bot.send_message(chat_id=chat_id, reply_to_message_id=update.message["message_id"], text="Yo!")

#     return {"ok": True}

