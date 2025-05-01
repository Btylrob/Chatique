import csv
import os
import time
import threading
import logging
import telebot
import json
import numpy as np
from dotenv import load_dotenv
from markupsafe import escape
from analyzetext import analyze_text

# Logger Module
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  

formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

info_handler = logging.FileHandler('app.log')
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(formatter)

error_handler = logging.FileHandler('app.log')
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

critical_handler = logging.FileHandler("app.log")
critical_handler.setLevel(logging.CRITICAL)
critical_handler.setFormatter(formatter)

if logger.hasHandlers():
    logger.handlers.clear()

# Add handlers to the logger
logger.addHandler(info_handler)
logger.addHandler(error_handler)
logger.addHandler(critical_handler)

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

rule_file_path = "rules.json"
flag_word_file_path = "flaggedwords.json"


def add_ban_list(user_id: int):
    """Add select user to the banned list."""
    banned_list.append(user_id)


@bot.message_handler(commands=['fw', 'flagword'])
def set_flagged_word(message):
    """Handles additional flagged word specific org might want to add"""
    bot.reply_to(message, "Type flagged word to add to register")
    bot.register_next_step_handler(message, process_flag_word)


@bot.message_handler(commands=['dr', 'deleterule'])
def delete_rule(message):
    """Handles deletion of said rule in json file"""
    bot.reply_to(message, "Type the number of which rule you want to delete")
    bot.register_next_step_handler(message, process_delete_rule)


@bot.message_handler(commands=['sr', 'setrulebook'])
def set_rule(message):
    bot.reply_to(message,
                 "Type Rules out in (1. ex. Rule format) for said group")
    bot.register_next_step_handler(message, process_rule_book)


@bot.message_handler(commands=['lb', 'listban'])
def list_banned_users(message):
    """Handles listing of all current banned members"""
    banned_array = np.array(banned_list)

    if len(banned_array) == 0:
        logger.info("No userids found in banned users list")
        bot.reply_to(message, "No userids found in banned log")
        return


@bot.message_handler(commands=['r', 'rules'])
def list_rules(message):
    """List rules that are stored in JSON"""
    try:
        with open(rule_file_path, 'r') as file:
            rules = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        rules = {}

    if not rules:
        logger.info("No set rules in rules list")
        bot.reply_to(message, "No rules found.")
        return

    formatted_rules = "\n".join(f"{idx+1}. {rule_Obj['rule']}"
                                for idx, rule_Obj in enumerate(rules.values()))
    bot.reply_to(message, f"📜 Group Rules:\n{formatted_rules}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the start cmd sending a welcome message"""
    logger.info(f"{message.from_user.id} started the start cmd")
    bot.reply_to(message,
                 "Welcome! 🎉 I’m your bot. How can I assist you today?")


@bot.message_handler(commands=['setban', 'sb'])
def set_ban_lenth(message):
    """Handles request to change alloted time for ban lengths"""
    bot.reply_to(message, "Type default ban lenght to set ")
    bot.register_next_step_handler(message, process_ban_length)


@bot.message_handler(commands=['sw', 'setwarning'])
def set_warning_threshold(message):
    """Handles request to set warning threshold"""
    bot.reply_to(message, "Type number for max length for default warnings")
    bot.register_next_step_handler(message, process_warn)


def process_delete_rule(message):
    """process deletion in json"""
    try:
        index_to_pop = int(message.text)
        with open(file_path, 'r') as file:
            rules = json.load(file)

        keys = list(rules.keys())
        if 0 <= index_to_pop < len(keys):
            removed_key = keys[index_to_pop]
            removed_rule = rules.pop(removed_key)

            with open("rules.json", 'w') as file:
                json.dump(rules, file, indent=4)
            logger.info(f"Rule {removed_rule} deleted from rules.json")
            bot.reply_to(message, f"Rule {removed_rule} deleted")

        else:
            logger.info("Invalid rule number inputted for deletion")
            bot.reply_to(message, "Rule number does not exist")

    except Exception as e:
        logger.error("Failed to delete rules")
        bot.reply_to(message, f"failed to delete error: {e}")


def process_warn(message):
    """Process warning threshold set by admin"""
    global warning_threshold
    try:
        warning_threshold = int(message.text)
        logger.info(f"Warning length set to {warning_threshold}")
        bot.reply_to(message, f"Warning length set to {warning_threshold}")
    except ValueError:
        logger.info("Invalid warning threshold length")
        bot.reply_to(message, "Invalid warning threshold length")


def process_ban_length(message):
    """Process ban length catch if user ban length is not real number"""
    global ban_length
    try:
        ban_length = int(message.text)
        logger.info(f"Ban length set to {ban_length} day/s")
        bot.reply_to(message, f"Ban lenght set to {ban_length} days.")
    except ValueError:
        logger.info("Invalid input set for ban length")
        bot.reply_to(message,
                     "Invalid ban legnth set please input a real number")


def process_flag_word(message):
    """insert flagged word into a json file"""
    new_flag = message.text.strip()  # strip space from json
    try:
        if os.path.exists(flag_word_file_path):
            with open(flag_word_file_path, 'r') as file:
                flags = json.load(file)
                if not isinstance(flags, list):
                    flags = []

        else:
            flags = []
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("flaggedwords.json not found in repository")
        flags = []

    if new_flag not in flags:
        flags.append(new_flag)

    with open(flag_word_file_path, 'w') as file:
        json.dump(flags, file, indent=4)

    logger.info(f"The word {new_flag} was added to the flaggedwords.json")
    bot.reply_to(message, f"Flagged word added {new_flag}")


def process_rule_book(message):
    """insert rule into json file"""
    new_rule = message.text.strip()
    try:
        if os.path.exists(rule_file_path):
            with open(rule_file_path, 'r') as file:
                rules = json.load(file)
        else:
            rules = {}
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("rules.json not found in repository")
        rules = {}

    new_key = f"rule_{len(rules) + 1}"
    rules[new_key] = {"rule": new_rule}

    with open(rule_file_path, 'w') as file:
        json.dump(rules, file, indent=4)

    logger.info(f"The rule {new_rule} was added to rules.json")
    bot.reply_to(message, f"Rule added: {new_rule}")


@bot.message_handler(func=lambda msg: True)
def analyze_and_respond(message):
    """Analyze and respond to all incoming message through telegram and pass warning functions"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    analysis_result = analyze_text(message.text)

    if "🚫 Hate Speech Detected" in analysis_result or "⚠️ Banned: Detected similar word" in analysis_result or "⚠️ Flagged Emoji Detected":
        user_warning[user_id] = user_warning.get(user_id, 0) + 1

    if warning_threshold is None or warning_threshold == 0:
        logger.info("No set warning threshold for users")
        bot.reply_to(message, "There is no current warning limit on users.")
        return

    if user_warning.get(user_id, 0) > warning_threshold:
        logger.info(
            f"{message.from_user.first_name} has been banned for {ban_length} days"
        )
        bot.reply_to(message, "user has been banned contents logged")
        bot.reply_to(
            message,
            f"At {time.ctime()} User: {message.from_user.first_name} has been warned over {warning_threshold} time to stop spreading vulgar language and hate speach. {message.from_user.first_name} will be banned until {ban_length}."
        )
        add_ban_list(message.from_user.first_name)
        bot.kick_chat_member(chat_id, user_id)
        return

    bot.reply_to(message, analysis_result)


# Keep the bot running
bot.infinity_polling()
