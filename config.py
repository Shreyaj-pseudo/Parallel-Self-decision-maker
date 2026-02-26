import os
from dotenv import load_dotenv
from backboard import BackboardClient

load_dotenv()

API_KEY = os.getenv("BACKBOARD_API_KEY")

client = BackboardClient(api_key=API_KEY)