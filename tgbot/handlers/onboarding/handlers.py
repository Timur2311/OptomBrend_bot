from cgitb import text
import datetime
from email.mime import audio
import imp, pprint
from dtb.settings import TELEGRAM_TOKEN
import logging, telegram
from tkinter.tix import Tree
from unicodedata import name
from turtle import up, update

from django.utils import timezone
from telegram import ParseMode, Update, Bot, Voice
from telegram.ext import CallbackContext
from tgbot.handlers.admin.handlers import admin

from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ChatMemberHandler,
    Filters, filters,
    ConversationHandler,
    CallbackContext,
)

from tgbot.handlers.utils.files import _get_file_id

admins = [1755197237,]

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
    
FILE, TYPING = range(2)

    

def start(update: Update, context: CallbackContext) -> int:
    """Starts the conversation and asks the user about their gender."""
    
    u, created = User.get_user_and_created(update, context)
    text = ""     

    if u.user_id in admins:
        text = "Siz ushbu botda adminsiz, guruhga o'tib mijozlarga javob yozing!"
        update.message.reply_text(text=text)        
        return TYPING
    else:
        if created:
            text = static_text.start_created.format(first_name=u.first_name)
        else:
            text = static_text.start_not_created.format(first_name=u.first_name)
        update.message.reply_text(text=text) 
        return FILE

    
    

def typing(update: Update, context: CallbackContext) -> int:     
    update_json = update.to_dict()    
    message = update.message
    text = update.message.text      
    # print(message)
    if not "reply_to_message" in update_json["message"]:
        return TYPING
    if not "forward_from" in update_json["message"]["reply_to_message"]:
        return TYPING
    
    to_customer = update_json["message"]["reply_to_message"]["forward_from"]["id"]   
    if message.location:
        update.message.bot.send_location(chat_id = to_customer, latitude = message.location.latitude, longitude = message.location.longitude )  
    elif message.voice:
        file_id = _get_file_id(update_json["message"])
        update.message.bot.send_voice(chat_id = to_customer, voice = file_id)
    elif message.audio: 
        file_id = _get_file_id(update_json["message"])
        update.message.bot.send_audio(chat_id = to_customer, audio = file_id)
    elif message.document: 
        file_id = _get_file_id(update_json["message"])
        update.message.bot.send_document(chat_id = to_customer, document = file_id)
    elif message.video: 
        file_id = _get_file_id(update_json["message"])
        update.message.bot.send_video(chat_id = to_customer, video = file_id)
    elif message.text:
        update.message.bot.send_message(chat_id = to_customer,text=text)   
    return TYPING
    
def file(update: Update, context: CallbackContext) -> int:
    
    u = User.get_user(update, context)
    if u.user_id not in admins:
        update_json = update.to_dict()
        message_id = update_json["message"]["message_id"]
        # if  "media_group_id" in update_json["message"]:
        #     print(u.is_blocked_bot)
        #     if u.is_blocked_bot:                
        #         update.message.reply_text(text='Murojaatingiz qabul qilindi! Javobni kuting...',parse_mode=telegram.ParseMode.HTML)
        #         u.is_blocked_bot = False
        #         u.save
        #     context.bot.forward_message(chat_id = '-1001572519768', from_chat_id = update.message.chat.id, message_id = message_id)

        #     print(u.is_blocked_bot)
        #     return MEDIA
            
        update.message.reply_text(
            text='Murojaatingiz qabul qilindi! Javobni kuting...',
            parse_mode=telegram.ParseMode.HTML,
            reply_to_message_id=message_id
        )
        context.bot.forward_message(chat_id = '-1001572519768', from_chat_id = update.message.chat.id, message_id = message_id)
    return FILE

# def media(update: Update, context: CallbackContext) -> int:
#     update.message.reply_text(text="media ga kirdi")
#     return FILE




def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            FILE:[MessageHandler(Filters.all, file)],
            TYPING:[MessageHandler(Filters.all , typing)],            
            # MEDIA:[MessageHandler(Filters.all, media)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=False,
        conversation_timeout=None,
        
        )
    