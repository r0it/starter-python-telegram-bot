import uvicorn
import config
from main import app, ptb

# Use polling when running locally
if __name__ == "__main__":
    if not config.ENV:
        print(f"Application started without webhook: {config.WEB_HOST}")
        ptb.run_polling(poll_interval=3)
    else:
        # Used for testing webhook locally, instructions for how to set up local webhook at https://dev.to/ibrarturi/how-to-test-webhooks-on-your-localhost-3b4f
        uvicorn.run(app, host="0.0.0.0", port=8181)