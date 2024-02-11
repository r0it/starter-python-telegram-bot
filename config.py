from os import getenv
from dotenv import load_dotenv

load_dotenv()

""" General config """
# Set ENV to any value to use webhook instead of polling for bot. Must be set in prod environment.
ENV = getenv("ENV")

""" Telegram config """
TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
TG_SECRET_TOKEN = getenv("TG_SECRET_TOKEN")
WEB_HOST = getenv("WEB_HOST")
WEB_URL = 'http://localhost:8181'
if WEB_HOST is not None:
    WEB_URL = WEB_HOST

""" Google Gemini config """
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
TRACK_FOOD_PROMPT = """
If you don't see any food items in the image, then just describe the image.
If you see ingredients list or Nutrient Facts table, based on that information explain if it is healthy or not.
If you see any food item in the image, then only do the following.
You are an expert in nutritionist where you need to see the food items from the image
               and calculate the total calories, also provide the details of every food items with calories intake
               is below format in descending order of calories

               1. Item 1 - no of calories
               2. Item 2 - no of calories
               ----
               ----
Finally, you can also mention whether the food is healthy or not and also mention the percentage split of the
carbs, fats and protein in below format in descending order of %
1. Carbs - %
2. Fats - %
3. Protein - %
"""
START_MSG = """
> **Welcome to the world of A.I.**
> 
>/scanMyImg (Upload any image)
> 
>/ama (Ask Me Anything)
"""
AMA_MSG = """
> **ama A.K.A. Ask Me Anything**
> 
> Eg. Write a 50 words essay on A.I.
> 
> /cancel to cancel the operation
"""
TIMEOUT_MSG = """
> Sorry, wait a minute before your next query.
"""
IMG_UPLOAD_MSG = """
> **Image analysis**
> 
> 1. Upload an image of any food item, to track calories
> 
> 2. Upload an image of food labels or ingridents to know if it is healthy or not
> 
> 3. Upload any other image to know more about it
>
> /cancel to cancel the operation
"""
CONVO_END_MSG = """\n\n
> **Enjoying?**
> 
>/scanMyImg (Upload any image)
> 
>/ama (Ask me anything)
"""

