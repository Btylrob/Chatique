import os
import time
import numpy as np
import telebot
from dotenv import load_dotenv
from analyzetext import analyze_text


load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# Variable for setting 
user_warning={}
warning_threshold= None
ban_length= None
banned_list=[]



# function to add banned accounts
def addbanlist(user_id):
    banned_list.append(user_id)

curtime = time.ctime(d)

# Handles listing of all current band members
@bot.message_handler(commands=['lb', 'listban'])
def list_ban(message):
    banned_array= np.array(banned_list)
    bot.reply_to(message, f"Current Members Banned As of {curtime}: {banned_array}")

# Handles /start command and sends a welcome message
@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! 🎉 I’m your bot. How can I assist you today?")

# Handles request to change and set alloted time for ban ban_length
@bot.message_handler(commands=['setban', 'sb'])
def set_ban(message):
    bot.reply_to(message, "Type default ban lenght to set ")
    bot.register_next_step_handler(message, process_ban_length)

#warning threshold handler
@bot.message_handler(commands=['sw', 'setwarning'])
def set_warn(message):
    bot.reply_to(message, "Type number for max length for default warnings")
    bot.register_next_step_handler(message, process_warn)

#process warning threshold 
def process_warn(message):
    global warning_threshold
    try:
        warning_threshold = int(message.text)
        bot.reply_to(message, f"Warning length set to {warning_threshold}")
    except ValueError:
        bot.reply_to(message, "Invalid warning threshold length")

#process ban length 
def process_ban_length(message):
    global ban_length
    try: 
        ban_length = int(message.text)
        bot.reply_to(message, f"Ban lenght set to {ban_length} minutes.")
    except ValueError: # If a inproper value inputed except message
        bot.reply_to(message, "Invalid Ban Length Set")
   

# analyze and respond to all incoming messages through telegram
@bot.message_handler(func=lambda msg: True)
def analyze_and_respond(message):
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