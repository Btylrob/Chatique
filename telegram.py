import os
import telebot
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# Handles /start command and sends a welcome message
@bot.message_handler(commands=['start', 'Start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome! 🎉 I’m your bot. How can I assist you today?")

# Handles commands /cm.kick and /cm.k
@bot.message_handler(commands=['cm.kick', 'cm.k'])
def handle_kick(message):
    bot.reply_to(message, "Howdy, how are you doing?")

# Keep the bot running
bot.infinity_polling()
