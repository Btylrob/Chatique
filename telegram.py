import os
import time
import threading
import telebot
import json
import numpy as np
from flask import Flask, render_template
from dotenv import load_dotenv
from markupsafe import escape
from analyzetext import analyze_text

# Load .env contents
load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

if BOT_TOKEN == None:
    raise ValueError("API key not found in env file.")
    exit(1)

print("API key retrieved from env")

bot = telebot.TeleBot(BOT_TOKEN)

# Variables for setting
user_warning = {}
warning_threshold = None
ban_length = None
banned_list = []
flagged_word = []
rule_book = ()

file_path = "rules.json"


def get_current_time():
    """Returns the current time as a string."""
    return time.ctime()


def add_ban_list(user_id: int):
    """Add select user to the banned list."""
    banned_list.append(user_id)

@bot.message_handler(commands=['fw', 'flagword'])
def set_flagged_word(message):
    """Handles additional flagged word specific org might want to add"""
    bot.reply_to(message, "Type flagged word to add to register")
    bot.register_next_step_handler(message, proccess_flag_word)

@bot.message_handler(commands=['dr', 'deleterule'])
def delete_rule(message):
    """Handles deletion of said rule in json file"""
    bot.reply_to(message, "Type the number of which rule you want to delete")
    bot.register_next_step_handler(message, process_delete_rule)

@bot.message_handler(commands=['sr', 'setrulebook'])
def set_rule(message):
    bot.reply_to(message, "Type Rules out in (1. ex. Rule format) for said group")
    bot.register_next_step_handler(message, process_rule_book)


@bot.message_handler(commands=['lb', 'listban'])
def list_ban(message):
    """Handles listing of all current banned members"""
    banned_array = np.array(banned_list)

    if len(banned_array) == 0:
        bot.reply_to(message, "No userids found in banned log")
        return

@bot.message_handler(commands=['r', 'rules'])
def list_rules(message):
    """List rules that are stored in JSON"""
    try:
        with open(file_path, 'r') as file:
            rules = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        rules = {}

    if not rules:
        bot.reply_to(message, "No rules found.")
        return

    formatted_rules = "\n".join(f"{idx+1}. {rule_Obj['rule']}" for idx, rule_Obj in enumerate(rules.values()))
    bot.reply_to(message, f"📜 Group Rules:\n{formatted_rules}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the start cmd sending a welcome message"""
    bot.reply_to(message,
                 "Welcome! 🎉 I’m your bot. How can I assist you today?")


@bot.message_handler(commands=['setban', 'sb'])
def set_ban(message):
    """Handles request to change alloted time for ban lengths"""
    bot.reply_to(message, "Type default ban lenght to set ")
    bot.register_next_step_handler(message, process_ban_length)


@bot.message_handler(commands=['sw', 'setwarning'])
def set_warn(message):
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
                json.dump(rules, file, indent= 4)
        
            bot.reply_to(message, f"Rule {removed_rule} deleted")

        else:
            bot.reply_to(message, "Rule number does not exist")

    except Exception as e:
        bot.reply_to(message, f"failed to delete error: {e}")


def process_warn(message):
    """Process warning threshold set by admin"""
    global warning_threshold
    try:
        warning_threshold = int(message.text)
        bot.reply_to(message, f"Warning length set to {warning_threshold}")
    except ValueError:
        bot.reply_to(message, "Invalid warning threshold length")


def process_ban_length(message):
    """Process ban length catch if user ban length is not real number"""
    global ban_length
    try:
        ban_length = int(message.text)
        bot.reply_to(message, f"Ban lenght set to {ban_length} days.")
    except ValueError:
        bot.reply_to(message,
                     "Invalid ban legnth set please input a real number")

def proccess_flag_word(message):
    """Process ban word insert ban word into an array"""
    global flagged_word
    try: 
        flagged_word = str(message.text)
        bot.reply_to(message, f"The word {flagged_word} is now added to the registry")
    except ValueError:
        bot.reply_to(message, "Please enter one word at a time")

def process_rule_book(message):
    """insert rule into json file"""
    new_rule = message.text.strip()
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                rules = json.load(file)
        else:
            rules = {}
    except (FileNotFoundError, json.JSONDecodeError):
        rules = {}
    
    new_key = f"rule_{len(rules) + 1}"
    rules[new_key] = {"rule": new_rule}

    with open(file_path, 'w') as file:
        json.dump(rules, file, indent=4)

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
        bot.reply_to(message, "There is no current warning limit on users.")
        return

    if user_warning.get(user_id, 0) > warning_threshold:
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
