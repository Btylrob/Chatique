from config import bot
from bot_commands import (
    send_welcome, set_flagged_word, delete_rule, set_rule,
    list_banned_users, list_rules, set_ban_lenth,
    set_warning_threshold, analyze_and_respond
)

def register_handlers():
    bot.message_handler(commands=['start'])(send_welcome)
    bot.message_handler(commands=['fw', 'flagword'])(set_flagged_word)
    bot.message_handler(commands=['dr', 'deleterule'])(delete_rule)
    bot.message_handler(commands=['sr', 'setrulebook'])(set_rule)
    bot.message_handler(commands=['lb', 'listban'])(list_banned_users)
    bot.message_handler(commands=['r', 'rules'])(list_rules)
    bot.message_handler(commands=['setban', 'sb'])(set_ban_lenth)
    bot.message_handler(commands=['sw', 'setwarning'])(set_warning_threshold)
    bot.message_handler(func=lambda msg: True)(analyze_and_respond)