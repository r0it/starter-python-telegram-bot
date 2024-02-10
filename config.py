from os import getenv
from dotenv import load_dotenv

load_dotenv()

""" General config """
# Set ENV to any value to use webhook instead of polling for bot. Must be set in prod environment.
ENV = getenv("ENV")

""" Telegram config """
TG_BOT_TOKEN = getenv("TG_BOT_TOKEN")
TG_SECRET_TOKEN = getenv("TG_SECRET_TOKEN")
CYCLIC_URL = getenv("CYCLIC_URL", 'http://localhost:8181')

""" Google Gemini config """
GOOGLE_API_KEY = getenv("GOOGLE_API_KEY")
TRACK_FOOD_PROMPT = """
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

