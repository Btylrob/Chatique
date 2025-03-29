import os
import time
import numpy as np
import telebot
from dotenv import load_dotenv
from analyzetext import analyze_text


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

def get_current_time():
    """Returns the current time as a string."""
    return time.ctime()


def add_ban_list(user_id: int):
    """Add select user to the banned list."""
    banned_list.append(user_id)


@bot.message_handler(commands=['lb', 'listban'])
def list_ban(message):
    """Handles listing of all current banned members"""
    banned_array = np.array(banned_list)

    if len(banned_array) == 0:
        bot.reply_to(message, "No userids found in banned log")
        return

    bot.reply_to(message, f"Current Members Banned As of {curtime}: {banned_array}")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handles the start cmd sending a welcome message"""
    bot.reply_to(message, "Welcome! 🎉 I’m your bot. How can I assist you today?")


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
        bot.reply_to(message, f"Ban lenght set to {ban_length} minutes.")
    except ValueError:
        bot.reply_to(message, "Invalid ban legnth set please input a real number")
   

@bot.message_handler(func=lambda msg: True)
def analyze_and_respond(message):
    """Analyze and respond to all incoming message through telegram and pass warning functions"""
    user_id = message.from_user.id
    analysis_result = analyze_text(message.text)
   
    if "🚫 Hate Speech Detected" in analysis_result or "⚠️ Banned: Detected similar word" in analysis_result:
        user_warning[user_id] = user_warning.get(user_id, 0) + 1

    if warning_threshold is None or warning_threshold == 0:
        bot.reply_to(message, "There is no current warning limit on users.")
        return

    if user_warning.get(user_id, 0) > warning_threshold:
        bot.reply_to(message, "user has been banned contents logged")
        bot.reply_to(message, f"At {curtime} User: {message.from_user.first_name} has been warned over {warning_threshold} time to stop spreading vulgar language and hate speach. {message.from_user.first_name} will be banned until {ban_length}.")
        addbanlist(message.from_user.first_name)
        return

    bot.reply_to(message, analysis_result)            

# Keep the bot running
bot.infinity_polling()