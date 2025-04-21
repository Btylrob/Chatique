import os
import time
import threading
import telebot
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

# Flask variables
app = Flask(__name__)


# Flask banned users page deployment
@app.route('/banned/')
def banned_users():
    """Flask route to display banned names."""
    global banned_list
    if not banned_list:
        return "no users in current banned list"
    return f"banned users: {', '.join(map(str, banned_list))}"


@app.errorhandler(404)
def page_not_found(e):
    """Return 404 page if error"""
    return render_template("404.html.jinja"), 404


def run_flask():
    """Flask page deployed local network for testing purposes"""
    if __name__ == "__main__":
        app.run(host="0.0.0.0", port=5000)
    else:
        bot.reply_to(message, "Failed to connect to port 5000")


# Deploy flask application on a seperate thread
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()


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


@bot.message_handler(commands=['lb', 'listban'])
def list_ban(message):
    """Handles listing of all current banned members"""
    banned_array = np.array(banned_list)

    if len(banned_array) == 0:
        bot.reply_to(message, "No userids found in banned log")
        return

    bot.reply_to(
        message,
        f"Click to view current banned members of pop http://10.0.0.73:5000/banned/"
    )


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
        bot.reply_to(message, f"Ban lenght set to {ban_length * 1440} days.")
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

@bot.message_handler(func=lambda msg: True)
def analyze_and_respond(message):
    """Analyze and respond to all incoming message through telegram and pass warning functions"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    analysis_result = analyze_text(message.text)

    if "🚫 Hate Speech Detected" in analysis_result or "⚠️ Banned: Detected similar word" in analysis_result:
        user_warning[user_id] = user_warning.get(user_id, 0) + 1

    if warning_threshold is None or warning_threshold == 0:
        bot.reply_to(message, "There is no current warning limit on users.")
        return

    if user_warning.get(user_id, 0) > warning_threshold:
        bot.reply_to(message, "user has been banned contents logged")
        bot.reply_to(
            message,
            f"At {time.ctime} User: {message.from_user.first_name} has been warned over {warning_threshold} time to stop spreading vulgar language and hate speach. {message.from_user.first_name} will be banned until {ban_length}."
        )
        add_ban_list(message.from_user.first_name)
        bot.kick_chat_member(chat_id, user_id)
        return

    bot.reply_to(message, analysis_result)


# Keep the bot running
bot.infinity_polling()
