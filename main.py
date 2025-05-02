from config import bot
from bot_handlers import register_handlers
from logger_config import logger

if __name__ == "__main__":
    logger.info("Bot is running")
    register_handlers()
    bot.infinity_polling()