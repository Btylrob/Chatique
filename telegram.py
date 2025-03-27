import os
import time
import telebot
from dotenv import load_dotenv
from app import analyze_text


load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

user_warning={}
warning_threshold= None
ban_length= None

curtime = time.ctime(1627908313.717886)


# Handles /start command and sends a welcome message
@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! 🎉 I’m your bot. How can I assist you today?")

# Handles request to change and set alloted time for ban ban_length
@bot.message_handler(commands=['setban', 'sb'])
def set_ban(message):
    bot.reply_to(message, "Type default ban lenght to set ")
    bot.register_next_step_handler(message, process_ban_length)

#process ban threshold lengh



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

        if user_warning[user_id] >= ban_threshold:
            bot.reply_to(message, "user has been banned contents logged")
            bot.reply_to(message, f"At {curtime} User: {message.from_user.first_name} has been warned over {ban_threshold} time to stop spreading vulgar language and hate speach. {message.from_user.first_name} will be banned until {ban_length}.")
            return

    bot.reply_to(message, analysis_result)            

# Keep the bot running
bot.infinity_polling()