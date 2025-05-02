import os
from dotenv import load_dotenv
import telebot
from logger_config import logger


# Load .env contents
load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

if BOT_TOKEN == None:
    logger.critical(
        "API key not found can not load successfully application will fail")
    exit(1)

logger.info("✅ API key successfully loaded from .env")

bot = telebot.TeleBot(BOT_TOKEN)

# Variables for setting
user_warning = {}
warning_threshold = None
ban_length = None
banned_list = []
flagged_word = []
rule_book = ()