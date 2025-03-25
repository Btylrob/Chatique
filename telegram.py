import os
import time
import telebot
from dotenv import load_dotenv
from app import analyze_text

load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

user_warning={}
ban_threshold=3

curtime = time.ctime(1627908313.717886)


# Handles /start command and sends a welcome message
@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! 🎉 I’m your bot. How can I assist you today?")

# analyze and respond to all incoming messages through telegram
@bot.message_handler(func=lambda msg: True)
def analyze_and_respond(message):
    user_id = message.from_user.id
    analysis_result = analyze_text(message.text)
   
    if "🚫 Hate Speech Detected" in analysis_result:
        user_warning[user_id] = user_warning.get(user_id, 0) + 1

        if user_warning[user_id] >= ban_threshold:
            bot.reply_to(message, "user has been banned contents logged")
            bot.reply_to(message, f"At {curtime} User: {message.from_user.first_name} has been warned over {ban_threshold} to stop spreading vulgar language and hate speach")
            return

    bot.reply_to(message, analysis_result)            

# Keep the bot running
bot.infinity_polling()
