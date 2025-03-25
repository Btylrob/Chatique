import os
import telebot
from dotenv import load_dotenv
from app.py import analyze_text

load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)


# Handles /start command and sends a welcome message
@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! 🎉 I’m your bot. How can I assist you today?")

# analyze and respond to all incoming messages through telegram
@bot.message_handler(func=lambda msg: True)
def analyze_and_respond(message):
    analysis_result = analyze_text(message.text)
    bot.reply_to(message, analysis_result)

# Keep the bot running
bot.infinity_polling()
