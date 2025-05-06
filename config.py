import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    CURRENT_RATE = os.getenv('CURRENT_RATE')
    ADMIN = os.getenv('ADMIN')
