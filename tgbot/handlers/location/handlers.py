import telegram
from telegram import Update
from telegram.ext import CallbackContext

from tgbot.handlers.location.static_text import share_location, thanks_for_location
from tgbot.handlers.location.keyboards import send_location_keyboard
from tgbot.models import User, Location


def ask_for_location(update: Update, context: CallbackContext) -> None:
    """ Entered /ask_location command"""
    u = User.get_user(update, context)

    context.bot.send_message(
        chat_id=u.user_id,
        text=share_location,
        reply_markup=send_location_keyboard()
    )


def location_handler(update: Update, context: CallbackContext) -> None:
    # receiving user's location
    u = User.get_user(update, context)
    update_json = update.to_dict()
    message_id = update_json["message"]["message_id"]
    lat, lon = update.message.location.latitude, update.message.location.longitude
    Location.objects.create(user=u, latitude=lat, longitude=lon)
    context.bot.forward_message(chat_id = '-1001572519768', from_chat_id = update.message.chat.id, message_id = message_id)
    
