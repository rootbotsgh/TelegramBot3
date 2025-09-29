import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
STORAGE_CHAT_ID = os.environ.get("STORAGE_CHAT_ID") # channel id
ADMIN_USER_ID = os.environ.get("ADMIN_USER_ID") # Replace with your actual Telegram user ID
DEFAULT_SUBJECTS = []

INDEX_FILE = "index.json"

#print(BOT_TOKEN)
#print(STORAGE_CHAT_ID)
#print(ADMIN_USER_ID)