import telebot
import datetime
import os

# Initialize the bot with the API token
bot = telebot.TeleBot(os.environ['TELEGRAM_BOT_TOKEN'])

# Dictionary to store the diary entries for each user
diaries = {}


# Function to handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    # Send a greeting message to the user
    bot.send_message(chat_id, "Hello! Welcome to the Diary Bot. Type /help to see a list of available commands.")

    # Initialize an empty diary for the user if they don't have one yet
    if chat_id not in diaries:
        diaries[chat_id] = []


# Function to handle the /help command
@bot.message_handler(commands=['help', 'h'])
def help(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if chat_id not in diaries:
        diaries[chat_id] = []

    # Send a list of available commands to the user
    bot.send_message(chat_id, "Here is a list of available commands:\n"
                              "/help - see a list of available commands\n"
                              "/add - add a new diary entry\n"
                              "/write - add text to an existing diary entry\n"
                              "/delete - delete an existing diary entry\n"
                              "/read - read an existing diary entry\n"
                              "/show - show all diary entries\n"
                              "You can also use the short commands 'h', 'a', 'w', 'd', 'r' and 's' instead of the full "
                              "commands.")


# Function to add a new diary entry
@bot.message_handler(commands=['add', 'a'])
def add_entry(message):
    # Get the user's chat ID and the current date
    chat_id = message.chat.id
    date = datetime.datetime.now().strftime("%Y-%m-%d")

    if chat_id not in diaries:
        diaries[chat_id] = []

    # Ask the user for the name of the diary entry
    bot.send_message(chat_id, "Enter a name for the diary entry. Type 'cancel' to cancel the operation:")
    bot.register_next_step_handler(message, add_entry_confirm, date)


# Function to confirm the creation of a new diary entry
def add_entry_confirm(message, date):
    # Get the user's chat ID and the name of the diary entry
    chat_id = message.chat.id
    name = message.text

    # Cancel the operation if user wants to
    if name.lower() == 'cancel':
        bot.send_message(chat_id, "Ok. Operation canceled.")
    else:
        # Create a new diary entry with the given name and date
        diaries[chat_id].append({
            "date": date,
            "name": name,
            "text": ""
        })

        # Send a confirmation message to the user
        bot.send_message(chat_id, "Diary entry '{}' created from {}.".format(name, date))


# Function to add text to an existing diary entry
@bot.message_handler(commands=['write', 'w'])
def write_text(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if chat_id not in diaries:
        diaries[chat_id] = []

    # Show the list of diary entries
    entries_text = "Diary entries:\n"
    for i, entry in enumerate(diaries[chat_id]):
        entries_text += "{}. {} - {}\n".format(i + 1, entry["date"], entry["name"])

    bot.send_message(chat_id, entries_text)

    # Ask the user which entry they want to add text to
    bot.send_message(chat_id, "Enter the number of the entry you want to add text to. Type 'cancel' to cancel the operation.")
    # Pass the message and the date of the selected diary entry to the next function
    bot.register_next_step_handler(message, write_text_confirm)


def write_text_confirm(message):
    # Get the user's chat ID and the text of their message
    chat_id = message.chat.id
    text = message.text

    # Check if the message is a valid number
    if text.isdigit():
        # Convert the message to an integer
        entry_num = int(text) - 1

        # Check if the entry number is valid
        if 0 <= entry_num < len(diaries[chat_id]):
            # Get the selected diary entry
            entry = diaries[chat_id][entry_num]

            # Ask the user for the text to add to the entry
            bot.send_message(chat_id, "Enter the text you want to add to the entry. Type 'cancel' to cancel the operation.")
            bot.register_next_step_handler(message, write_text_save, entry_num)
        else:
            # Send an error message if the entry number is invalid
            bot.send_message(chat_id, "Entry number is not in range. Operation canceled.")
    else:
        if text.lower() == 'cancel':
            bot.send_message(chat_id, "Ok. Operation canceled.")
        else:
            # Send an error message if the message is not a valid number
            bot.send_message(chat_id, "Invalid input. Operation canceled.")


def write_text_save(message, entry_num):
    # Get the user's chat ID and the text of their message
    chat_id = message.chat.id
    text = message.text

    # Go back if user wants to
    if text.lower() == 'cancel':
        bot.send_message(chat_id, "Ok. Operation canceled.")
    else:
        # Add the text to diary
        diaries[chat_id][entry_num]["text"] += text + '\n'

        bot.send_message(chat_id, "The text added to selected diary entry.")


# Function to delete an existing diary entry
@bot.message_handler(commands=['delete', 'd'])
def delete_entry(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if chat_id not in diaries:
        diaries[chat_id] = []

    # Show the list of diary entries
    entries_text = "Diary entries:\n"
    for i, entry in enumerate(diaries[chat_id]):
        entries_text += "{}. {} - {}\n".format(i + 1, entry["date"], entry["name"])
    bot.send_message(chat_id, entries_text)

    # Ask the user which entry they want to delete
    bot.send_message(chat_id, "Enter the number of the entry you want to delete. Type 'cancel' to cancel the operation.")
    bot.register_next_step_handler(message, delete_entry_confirm)


# Function to confirm the deletion of an existing diary entry
def delete_entry_confirm(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if message.text.isdigit():
        # Get the number of the entry to be deleted
        entry_num = int(message.text) - 1

        if 0 <= entry_num < len(diaries[chat_id]):
            # Get the date and name of the diary entry
            date = diaries[chat_id][entry_num]["date"]
            name = diaries[chat_id][entry_num]["name"]

            # Ask the user for confirmation
            bot.send_message(chat_id,
                             "Are you sure you want to delete diary entry '{}' from {}? Type 'yes' to confirm.".format(name,
                                                                                                                      date))
            bot.register_next_step_handler(message, delete_entry_execute, entry_num)
        else:
            # Send an error message if the entry number is invalid
            bot.send_message(chat_id, "Entry number is not in range. Operation canceled.")
    else:
        if message.text.lower() == 'cancel':
            bot.send_message(chat_id, "Ok. Operation canceled.")
        else:
            # Send an error message if the message is not a valid number
            bot.send_message(chat_id, "Invalid input. Operation canceled.")


# Function to execute the deletion of an existing diary entry
def delete_entry_execute(message, entry_num):
    # Get the user's chat ID
    chat_id = message.chat.id

    # Check if the user confirmed the deletion
    if message.text.lower() == "yes":
        # Delete the diary entry
        del diaries[chat_id][entry_num]
        bot.send_message(chat_id, "Diary entry deleted.")
    else:
        # Send a message indicating that the deletion was cancelled
        bot.send_message(chat_id, "Deletion cancelled.")


# Function to read existing diary entries
@bot.message_handler(commands=['read', 'r'])
def read_entry(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if chat_id not in diaries:
        diaries[chat_id] = []

    # Show the list of diary entries
    entries_text = "Diary entries:\n"
    for i, entry in enumerate(diaries[chat_id]):
        entries_text += "{}. {} - {}\n".format(i + 1, entry["date"], entry["name"])
    bot.send_message(chat_id, entries_text)

    # Ask the user which entry they want to read
    bot.send_message(chat_id, "Enter the number of the entry you want to read. Type 'cancel' to cancel the operation.")
    bot.register_next_step_handler(message, read_entry_confirm)


# Function to confirm reading
def read_entry_confirm(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if message.text.isdigit():
        # Get the number of the entry to be deleted
        entry_num = int(message.text) - 1

        if 0 <= entry_num < len(diaries[chat_id]):
            # Get the number of the entry to be deleted
            entry_num = int(message.text) - 1

            # Show the text
            entry_text = "The text of selected diary entry:\n" + diaries[chat_id][entry_num]["text"]
            bot.send_message(chat_id, entry_text)
        else:
            # Send an error message if the entry number is invalid
            bot.send_message(chat_id, "Entry number is not in range. Operation canceled.")
    else:
        if message.text.lower() == 'cancel':
            bot.send_message(chat_id, "Ok. Operation canceled.")
        else:
            # Send an error message if the message is not a valid number
            bot.send_message(chat_id, "Invalid input. Operation canceled.")


# Function to show existing diary entries
@bot.message_handler(commands=['show', 's'])
def show_entries(message):
    # Get the user's chat ID
    chat_id = message.chat.id

    if chat_id not in diaries:
        diaries[chat_id] = []

    # Show the list of diary entries
    entries_text = "Diary entries:\n"
    for i, entry in enumerate(diaries[chat_id]):
        entries_text += "{}. {} - {}\n".format(i + 1, entry["date"], entry["name"])
    bot.send_message(chat_id, entries_text)


# Start the bot
bot.polling()
