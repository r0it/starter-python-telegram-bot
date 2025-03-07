# Python Telegram Bot Starter

This is simple Python Telegram Bot.


## Deploy to Cyclic in seconds 

[![Deploy to Cyclic](https://deploy.cyclic.app/button.svg)](https://deploy.cyclic.app/)

1) Set `server.py` as your entry point.
1) Create a new Telegram bot using [BotFather](https://t.me/botfather)
1) Store the bot token into a BOT_TOKEN environment variable
1) Create a SECRET_TOKEN and set it in the SECRET_TOKEN environment variable
1) Create a WEB_HOST env variable and set the current web host url
1) Create ENV env variable and set the value as "PROD"
1) Run the following curl substituting the appropriate variables to set the new webhook:
    ```
    curl https://api.telegram.org/bot${SECRET_TOKEN}/setWebhook \
        -F "url=https://${WEB_HOST}/webhook/"
    ```
1) Message you bot with `/start` or just say `Hello!`
1) Check your bot's status: `https://api.telegram.org/bot${SECRET_TOKEN}/getWebhookInfo`
1) To delete web hook : `https://api.telegram.org/bot${SECRET_TOKEN}/deleteWebhook?drop_pending_updates=true`

## Run Locally

Prerequisites:
- pyenv
- python 3.10.11

Install: `bin/install`
- creates virtual env
- installs dependencies from `requirements.txt`

Run: `bin/dev`
- runs a `uvicorn` server in reload mode

Run: `bin/start`
- runs a `uvicorn` server


## Helpful Docs:
- [python-telegram-bot](https://docs.python-telegram-bot.org/en/stable/index.html)
- [Telegram Bots API](https://core.telegram.org/bots/api)


## Questions / Help

Join us on Discord: [https://discord.cyclic.sh](https://discord.cyclic.sh)

Enjoy!
