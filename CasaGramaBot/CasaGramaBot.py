#!/usr/local/bin python3.7
# -*- coding: utf-8 -*-

# Commands for the @BotFather
# start - start the CasaGramaBot
# interactions - show actions on IoT devices
# help - show help dialogue

import os.path
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import CosmosDBHelper as dbhelper
import SendCloudToDeviceMessage as c2d
import logging


# Initialize Logging
# Output dir has to be set to system log path
output_dir = "$LOGPATH"
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOG = logging.getLogger()
LOG.setLevel(logging.INFO)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    handlers=[
                        logging.FileHandler(os.path.join(output_dir, "logs.log")),
                        logging.StreamHandler()
                    ])


# Static Variables to access Azure Cosmos DB
with open('properties/COSMOSDB_URI.txt', 'r') as uri_file:
    COSMOS_URI = uri_file.read()
with open('properties/COSMOSDB_READKEY.txt', 'r') as key_file:
    COSMOS_KEY = key_file.read()


# Shows /start command dialogue
def start(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    text = "Welcome to the CasaGramaBot! \nYou can type /interactions to see what actions you can perform. " \
           "\nTo see a list of commands, type /help."

    context.bot.send_message(chat_id=chatid, text=text)
    LOG.info("User [%s][%s]: sent /start command ", username, chatid)


# Predefined Interaction Buttons

def light_on(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    LOG.info("User [%s][%s]: sent /light_on command ", username, chatid)
    context.bot.send_message(chat_id=chatid, text="Light will be turned on")

    c2d.iothub_message_raspberry("led on")


def light_off(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    LOG.info("User [%s][%s]: sent /light_off command ", username, chatid)
    context.bot.send_message(chat_id=chatid, text="Light will be turned off")

    c2d.iothub_message_raspberry("led off")


def weather_data(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    LOG.info("User [%s][%s]: sent /weather_data command ", username, chatid)

    last_entry = dbhelper.get_last_entry(COSMOS_URI, COSMOS_KEY)
    id = dbhelper.get_deviceid(last_entry)
    ts = dbhelper.get_timestamp(last_entry)
    temp = dbhelper.get_temperature(last_entry)
    hum = dbhelper.get_humidity(last_entry)
    LOG.info("Weatherdata received for %s [%s]", id, ts)

    output = ts + "\n\nTemperature: \n" + temp + " °C \nHumidity: \n" + hum + " %"

    context.bot.send_message(chat_id=chatid, text=output)


# Shows /interactions keyboard with actions on the IoT devices

def interactions(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    interactions_text = "Choose an action you want to perform: \n" \
                        "/light_on - Turns the light on \n" \
                        "/light_off - Turns the light off \n" \
                        "/weather_data - Returns the recent weather data"
    light_on_button = telegram.KeyboardButton('/light_on')
    light_off_button = telegram.KeyboardButton('/light_off')
    weather_data_button = telegram.KeyboardButton('/weather_data')

    interactions_keyboard = [[light_on_button, light_off_button],
                            [weather_data_button]]
    reply_markup = telegram.ReplyKeyboardMarkup(interactions_keyboard, resize_keyboard=True, one_time_keyboard=True)
    context.bot.send_message(chat_id=chatid, text=interactions_text, reply_markup=reply_markup)

    LOG.info("User [%s][%s]: sent /interactions command", username, chatid)


# Shows /help command dialogue
def help(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id

    helptext = "/interactions - Show commands keyboard\n" \
               "/light_on - Turn light on\n" \
               "/light_off - Turn light off\n" \
               "/weather_data - Show latest weatherdata"

    context.bot.send_message(chat_id=chatid, text=helptext)
    LOG.info("User [%s][%s]: sent /help command", username, chatid)


# Logs user input (if text) to the logging console
def userinput(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    text = update.message.text
    LOG.info("User [%s][%s]: sent text [%s]", username, chatid, text)


# Sends dialogue for unknown commands
def unknown(update, context):
    username = update.message.from_user.username
    chatid = update.message.chat_id
    text = update.message.text

    context.bot.send_message(chat_id=chatid, text="Sorry, that command is unknown to me.")
    LOG.info("User [%s][%s]: sent unknown command [%s]", username, chatid, text)


def main():
    #  Static Variable for the Bot Token
    with open('properties/TOKEN.txt', 'r') as tokenfile:
        BOT_TOKEN = tokenfile.read()
    # Updater gets all updates invoked with 'getUpdates' that the user sends to the bot
    updater = Updater(token=BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('light_on', light_on))
    dispatcher.add_handler(CommandHandler('light_off', light_off))
    dispatcher.add_handler(CommandHandler('weather_data', weather_data))
    dispatcher.add_handler(CommandHandler('interactions', interactions))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(MessageHandler(Filters.text, userinput))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    updater.start_polling()


if __name__ == '__main__':
    main()
