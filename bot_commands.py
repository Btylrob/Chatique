import os
import json
import html
import time
import mistune
import analyzetext
from config import bot, user_warning, warning_threshold, ban_length, banned_list
from logger_config import logger
from telebot import types
from analyzetext import *

rule_file_path = "rules.json"
flag_word_file_path = "flaggedwords.json"

# Handler Functions


def toggle_urls():
    """toggles url detection"""
    analyzetext.url = bool(1 - analyzetext.url)
    new_state = "OFF ❌" if analyzetext.url else "ON ✅"
    logger.info(f"set to {url}")
    return f"Url Detection is now {new_state}"


def toggle_emojis():
    """Toggles 18+ emoji detection and returns the new state as text"""
    analyzetext.nsfwemoji = bool(1 - analyzetext.nsfwemoji)
    new_state = "OFF ❌" if analyzetext.nsfwemoji else "ON ✅"
    logger.info(f"NSFW emoji detection set to: {new_state}")
    return f"18+ Emoji Detection is now {new_state}"


def add_ban_list(user_id: int):
    """Add select user to the banned list."""
    banned_list.append(user_id)


def set_flagged_word(message):
    """Handles additional flagged word specific org might want to add"""
    bot.reply_to(message, "Type flagged word to add to register")
    bot.register_next_step_handler(message, process_flag_word)


def delete_rule(message):
    """Handles deletion of said rule in json file"""
    bot.reply_to(message, "Type the number of which rule you want to delete")
    bot.register_next_step_handler(message, process_delete_rule)


def set_rule(message):
    bot.reply_to(message,
                 "Type Rules out in (1. ex. Rule format) for said group")
    bot.register_next_step_handler(message, process_rule_book)


def list_banned_users(message):
    """Handles listing of all current banned members"""
    banned_array = np.array(banned_list)

    if len(banned_array) == 0:
        logger.info("No userids found in banned users list")
        bot.reply_to(message, "No userids found in banned log")
        return


def list_rules(message):
    """List rules that are stored in JSON"""
    try:
        with open(rule_file_path, 'r') as f:
            rules = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        rules = {}

    if not rules:
        logger.info("No set rules in rules list")
        bot.reply_to(message, "No rules found.")
        return

    formatted_rules = "\n".join(f"{idx+1}. {rule_Obj['rule']}"
                                for idx, rule_Obj in enumerate(rules.values()))
    bot.reply_to(message, f"📜 Group Rules:\n{formatted_rules}")


def chatique_help(message):
    """Handles execution of user custom submitted markdown rules page"""
    logger.info(f"{message.from_user.id} started the markdown rule cmd")

    def escape_markdown(text):
        """Escape only the necessary characters for MarkdownV2"""
        escape_chars = r'[]()~`>#+-=|{}.!\\'
        return ''.join(['\\' + c if c in escape_chars else c for c in text])

    try:
        with open('help.txt', 'r', encoding='utf-8') as f:
            raw_md = f.read()
            logger.info("help.txt opened")

        safe_text = escape_markdown(raw_md)

        logger.debug(safe_text)  # Check to see if it will pass in markdown

        bot.send_message(
            chat_id=message.chat.id,
            text=safe_text,
            parse_mode='MarkdownV2'  # Telegram interpets as md
        )
    except OSError as e:
        logger.error(f"help.txt.txt unable to be opened: {e}")
        bot.send_message(chat_id=message.chat.id,
                         text="❌ Failed to load the rules document.")


def send_welcome(message):
    """Handles the start cmd sending a welcome message"""
    logger.info(f"{message.from_user.id} started the start cmd")
    bot.reply_to(message,
                 "Welcome! 🎉 I’m your bot. How can I assist you today?")


def set_ban_length(message):
    """Handles request to change alloted time for ban lengths"""
    bot.reply_to(message, "Type default ban lenght to set ")
    bot.register_next_step_handler(message, process_ban_length)


def set_warning_threshold(message):
    """Handles request to set warning threshold"""
    bot.reply_to(message, "Type number for max length for default warnings")
    bot.register_next_step_handler(message, process_warn)


def process_delete_rule(message):
    """process deletion in json"""
    try:
        index_to_pop = int(message.text)
        with open(file_path, 'r') as f:
            rules = json.load(f)

        keys = list(rules.keys())
        if 0 <= index_to_pop < len(keys):
            removed_key = keys[index_to_pop]
            removed_rule = rules.pop(removed_key)

            with open("rules.json", 'w') as f:
                json.dump(rules, f, indent=4)
            logger.info(f"Rule {removed_rule} deleted from rules.json")
            bot.reply_to(message, f"Rule {removed_rule} deleted")

        else:
            logger.info("Invalid rule number inputted for deletion")
            bot.reply_to(message, "Rule number does not exist")

    except Exception as e:
        logger.error("Failed to delete rules")
        bot.reply_to(message, f"failed to delete error: {e}")


def process_warn(message):
    """Process warning threshold set by admin"""
    global warning_threshold
    try:
        warning_threshold = int(message.text)
        logger.info(f"Warning length set to {warning_threshold}")
        bot.reply_to(message, f"Warning length set to {warning_threshold}")
    except ValueError:
        logger.info("Invalid warning threshold length")
        bot.reply_to(message, "Invalid warning threshold length")


def process_ban_length(message):
    """Process ban length catch if user ban length is not real number"""
    global ban_length
    try:
        ban_length = int(message.text)
        logger.info(f"Ban length set to {ban_length} day/s")
        bot.reply_to(message, f"Ban lenght set to {ban_length} days.")
    except ValueError:
        logger.info("Invalid input set for ban length")
        bot.reply_to(message,
                     "Invalid ban legnth set please input a real number")


def process_flag_word(message):
    """insert flagged word into a json file"""
    new_flag = message.text.strip()  # strip space from json
    try:
        if os.path.exists(flag_word_file_path):
            with open(flag_word_file_path, 'r') as f:
                flags = json.load(f)
                if not isinstance(flags, list):
                    flags = []

        else:
            flags = []
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("flaggedwords.json not found in repository")
        flags = []

    if new_flag not in flags:
        flags.append(new_flag)

    with open(flag_word_file_path, 'w') as f:
        json.dump(flags, f, indent=4)

    logger.info(f"The word {new_flag} was added to the flaggedwords.json")
    bot.reply_to(message, f"Flagged word added {new_flag}")


def process_rule_book(message):
    """insert rule into json file"""
    new_rule = message.text.strip()
    try:
        if os.path.exists(rule_file_path):
            with open(rule_file_path, 'r') as f:
                rules = json.load(f)
        else:
            rules = {}
    except (FileNotFoundError, json.JSONDecodeError):
        logger.error("rules.json not found in repository")
        rules = {}

    new_key = f"rule_{len(rules) + 1}"
    rules[new_key] = {"rule": new_rule}

    with open(rule_file_path, 'w') as f:
        json.dump(rules, f, indent=4)

    logger.info(f"The rule {new_rule} was added to rules.json")
    bot.reply_to(message, f"Rule added: {new_rule}")

# button menus
@bot.message_handler(commands=['toggle_emojis'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text="18+ Emoji Detection", callback_data="toggle_emoji_btn")
    markup.add(btn)
    bot.send_message(message.chat.id, "Toggle Menu:", reply_markup=markup)

# Button handler
@bot.callback_query_handler(func=lambda call: call.data == "toggle_emoji_btn")
def callback_hello(call):
    result = toggle_emojis()
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=result)

def analyze_and_respond(message):
    """Analyze and respond to incoming Telegram message and apply warning logic"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    analysis_result = analyze_text(message.text)

    # Handle unset warning threshold
    if warning_threshold is None or warning_threshold == 0:
        logger.info("No set warning threshold for users")
        bot.reply_to(message, "There is no current warning limit on users.")
        return

    # Check for flagged content
    if ("🚫 Hate Speech Detected" in analysis_result
            or "⚠️ Banned: Detected similar word" in analysis_result
            or "⚠️ Flagged Emoji Detected" in analysis_result
            or "⚠️ Flagged URL Detected" in analysis_result):
        user_warning[user_id] = user_warning.get(user_id, 0) + 1
        logger.info(f"User {user_id} warning count: {user_warning[user_id]}")

        if user_warning[user_id] > warning_threshold:
            logger.info(
                f"{message.from_user.first_name} has been banned for {ban_length} days"
            )
            bot.reply_to(message, "User has been banned. Contents logged.")
            bot.reply_to(
                message,
                f"At {time.ctime()}, user {message.from_user.first_name} exceeded the warning threshold ({warning_threshold}) "
                f"for vulgar or hateful content. Banned until {ban_length} days from now."
            )
            add_ban_list(message.from_user.first_name)
            bot.kick_chat_member(chat_id, user_id)
            return



    # Normal reply if not banned
    bot.reply_to(message, analysis_result)
