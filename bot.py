# Python Packages
from ctypes import resize
from re import X
import requests
import os
from pyrsistent import m
import requests
import json
from dotenv import load_dotenv
import pandas as pd
import geopandas as gpd
from geopy.geocoders import Nominatim
import warnings
warnings.filterwarnings("ignore")
import random

# Telegram Bot Packages
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Update, KeyboardButton
from telegram.ext import ApplicationBuilder, ConversationHandler, CallbackQueryHandler, CommandHandler, MessageHandler, filters, Updater

# Local Modules
from database import (
    session_engine_from_connection_string,
    Item
)
from utilities import (
    # BINS_GDF, 
    # find_nearest_bin_location,
    convert_row_to_dict
)

############################################ Load Tokens / API KEYS

load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
CAT_API_KEY = os.getenv('CAT_API_KEY')
POSTGRESQL_CONNECTION_STRING = os.getenv('POSTGRESQL_CONNECTION_STRING')

############################################ Setup DB Connection

if (POSTGRESQL_CONNECTION_STRING ):
    session, engine = session_engine_from_connection_string(POSTGRESQL_CONNECTION_STRING)
else:
    session, engine = session_engine_from_connection_string(None)

#### Setup Geolocator (For Geocoding)
geolocator = Nominatim(user_agent="myGeocoder")

############################################ Print Log in Terminal
import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

############################################ Commands To Be Removed [1]

async def hello(update, context):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}')

async def quiz(update, context):
    session, engine = session_engine_from_connection_string(POSTGRESQL_CONNECTION_STRING)
    id = update.effective_chat.id
    score = 0

    data1 = "select item_name, disposal_instruction, image_url, is_recyclable from item"
    data2 = "select distinct disposal_instruction from item"

    query1 = session.execute(data1)
    query2 = session.execute(data2)

    info = query1.all()
    unique_instructions = query2.all()
    random.shuffle(info)
    random.shuffle(unique_instructions)

    selectedQn = random.choice(info)
    
    qnType = random.randint(0,1)

    if qnType == 0:
        item_name = selectedQn[0]
        img_url = selectedQn[2]
        is_recyclable = selectedQn[3]

        keyboard=[]

        if is_recyclable == True:
            keyboard = [[
            InlineKeyboardButton("Yes", callback_data="Correct!"),
            InlineKeyboardButton("No", callback_data="Incorrect. This item is actually recyclable."),
            ]]
        elif is_recyclable == False:
            keyboard = [[
            InlineKeyboardButton("Yes", callback_data="Incorrect. This item is not recyclable."),
            InlineKeyboardButton("No", callback_data="Correct!"),
            ]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("Is this item recyclable?")
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url, caption=item_name, reply_markup=reply_markup)


    else:
        item_name = selectedQn[0]
        img_url = selectedQn[2]
        is_recyclable = selectedQn[3]
        correct_ans = selectedQn[1]

        choices = []
        choices.append(correct_ans)

        while len(choices) < 3:
            rand_choice = random.choice(unique_instructions)
            if type(rand_choice) != str:
                rand_choice = rand_choice[0]
            if rand_choice not in choices:
                choices.append(rand_choice)

        keyboard = []
        random.shuffle(choices)

        for c in choices:
            if c == correct_ans:
                reply = "Correct!"
                keyboard.append([InlineKeyboardButton(c, callback_data=reply)])

            else:
                reply = "Incorrect. "
                if correct_ans == "Can be recycled at specific collection points":
                    reply = "Incorrect. It can be recycled at specific collection points."
                else:
                    reply = "Incorrect. You should " + correct_ans.lower() + "."

                keyboard.append([InlineKeyboardButton(c, callback_data=reply)])

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text("What is the proper way to dispose this item?")
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img_url, caption=item_name, reply_markup=reply_markup)

    return QUIZ_RESPONSE

            
QUIZ_RESPONSE = range(1)
async def disposeAns(update, context):

    query = update.callback_query
    await query.answer()
    ans = query.data


    chat_id=update.effective_chat.id
    await context.bot.send_message(chat_id, text=ans)
    return ConversationHandler.END


############################################ Get List of Items
RECYCLABLE_RESPONSE = range(1)
async def checkIfRecyclable(update, context):
    sql = "SELECT distinct category from item"
    query = session.execute(sql)
    categories = query.all()
    keyboard = []
    for category in categories:
        keyboard.append([InlineKeyboardButton(category[0], callback_data=category[0])]) 

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Please choose a category:", reply_markup=reply_markup)
    return RECYCLABLE_RESPONSE
    
    

def convertTuple(tup):
        # initialize an empty string
    str = ''
    for item in tup:
        str = str + item
    return str


async def getRecyclableItems(update, context):
    
    query = update.callback_query
    await query.answer()
    category = query.data

    sql = "SELECT item_name, is_recyclable from item where category = :cat"
    query = session.execute(sql, {"cat": category})
    items = query.all()

    print_item = f"List of {category} Items:\n"
    if len(items) == 0:
        print_item = "Sorry, no item is found for this category"
    else:
        for i in range(len(items)):
            if items[i][1]:
                display_name = items[i][0] + " ✅"
            else:
                display_name = items[i][0] + " ❌"

            print_item += "\n" + str(i+1) + ". " + display_name
            # print_item += "\n" + str(i+1) +". "+  convertTuple(items[i])

    chat_id=update.effective_chat.id
    await context.bot.send_message(chat_id, text=print_item)
    return ConversationHandler.END
    


############################################ Get Nearest Location of Bin

LOCATION_ONE, LOCATION_TWO = range(2)

async def getUserLocation(update, context):
    # keyboard = [
    #     KeyboardButton("Share My Location", callback_data="Share", request_location=True),
    #     KeyboardButton("Type My Location", callback_data="Type"),
    # ]
    # print(keyboard)
    # reply_markup = ReplyKeyboardMarkup(keyboard)

    ### [Not Able to Request Location, Share Location Feature Removed]
    # reply_markup = ReplyKeyboardMarkup([
    #         [KeyboardButton("Share My Location", callback_data="Share", request_location=True)],
    #         [KeyboardButton("Type My Location", callback_data="Type")]
    # ])
    
    # await update.message.reply_text(text='Tell us where are you now!', reply_markup=reply_markup)

    await update.message.reply_text(text='Tell us where are you now! \n\nTry to be more specific to obtain a more accurate result 😃')
    return LOCATION_ONE


### [Not Able to Request Location, Share Location Feature Removed]
# async def getLocation(update, context):
    # await update.message.reply_text(text='Tell us where are you now! \n\nTry to be as specific as you can, thanks! :)')
    # return LOCATION_TWO

# async def generateLocation(update, context):
#     longitude = update.message.longitude
#     latitude = update.message.latitude
    # nearest_bin_location, nearest_bin_lon, nearest_bin_lat  = find_nearest_bin_location(BINS_GDF, longitude, latitude)
    # await update.message.reply_text(f'Nearest Bin Location: {nearest_bin_location}')
    # await update.message.reply_text(f'https://maps.google.com/?q={nearest_bin_lat},{nearest_bin_lon}')
    # return ConversationHandler.END


async def getNearestBinLocation(update, context):
    input = update.message.text
    location = geolocator.geocode(input)

    if location:
        latitude = location.latitude
        longitude = location.longitude
        nearest_bin_location, nearest_bin_lon, nearest_bin_lat  = find_nearest_bin_location(BINS_GDF, longitude, latitude)
        await update.message.reply_text(f'Nearest Bin Location ♻️🗑:\n\n{nearest_bin_location}')
        await update.message.reply_text(f'https://maps.google.com/?q={nearest_bin_lat},{nearest_bin_lon}')
        return ConversationHandler.END

    else:
        await update.message.reply_text(f'Unable to find specified location, Try again!')
        return LOCATION_TWO


############################################ Building of Bot

bot = ApplicationBuilder().token(BOT_TOKEN).build()

# settings_handler = ConversationHandler(
#         entry_points=[CommandHandler("settings", saveUser)],
#         states={
#             BREED: [MessageHandler(filters.Regex("""^(All of them!|
#                                                       Bengal|
#                                                       Persian|
#                                                       Munchkin|
#                                                       Ragamuffin|
#                                                       Burmese|
#                                                       Russian Blue|
#                                                       Maine Coon|
#                                                       Abyssinian)$"""), saveBreed)],

#             NO_OF_PHOTOS: [
#                             MessageHandler(filters.TEXT & filters.Regex("[1-9]"), saveNoOfPhotos), 
#                             MessageHandler(~(filters.TEXT & filters.Regex("[1-9]")), invalidPhotoNo)
#                           ],

#             GIF: [
#                 MessageHandler(filters.TEXT & filters.Regex("^(GIF|JPG)$"), saveGif),
#             ],
#         },
#         fallbacks=[CommandHandler("cancel", cancel)],
#     )
async def cancel(update, context):
    user = update.message.from_user
    await update.message.reply_text(
        "Ok, we'll stop saving your settings", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

bot.add_handler(CommandHandler("hello", hello))
locations_handler = ConversationHandler(
    entry_points=[CommandHandler('findNearestBin', getUserLocation)],
    states={
        LOCATION_ONE: [
            MessageHandler(filters.TEXT, getNearestBinLocation)
        ],
        LOCATION_TWO: [
            MessageHandler(filters.TEXT, getNearestBinLocation)
        ]
    }, fallbacks=[CommandHandler("cancel", cancel)]
)
bot.add_handler(locations_handler)
checkRecyclable_handler = ConversationHandler(
    entry_points=[CommandHandler("checkIfRecyclable", checkIfRecyclable)],
    states={RECYCLABLE_RESPONSE: [CallbackQueryHandler(getRecyclableItems)]}, fallbacks=[CommandHandler("cancel", cancel)]
)
quiz_handler = ConversationHandler(
    entry_points=[CommandHandler("quiz", quiz)],
    states={QUIZ_RESPONSE: [CallbackQueryHandler(disposeAns)]}, fallbacks=[CommandHandler("cancel", cancel)]
)
bot.add_handler(checkRecyclable_handler)
bot.add_handler(quiz_handler)


bot.run_polling()