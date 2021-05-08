""" Deletion """
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

from .misc_commands import r
from .constants import ADMIN, DELETE_USER

def select_user_to_delete(update: Update, _: CallbackContext) -> int:
    """ select user """
    if str(update.message.from_user.id) != ADMIN:
        return ConversationHandler.END
    keys = r.keys(pattern="*")
    keyboard = []
    for key in keys:
        name = r.hget(key, "name")
        if key != ADMIN:
            keyboard.append([InlineKeyboardButton(name, callback_data=key)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(text='Spieler auswählen: ', reply_markup=reply_markup)
    return DELETE_USER

def delete_user(update: Update, _: CallbackContext) -> int:
    """ delete user """
    query = update.callback_query
    query.answer()
    user_id_to_delete = query.data
    user_name_to_delete = r.hget(user_id_to_delete, "name")
    r.delete(user_id_to_delete)
    query.edit_message_text(text = f'Spieler {user_name_to_delete} entfernt.')
    return ConversationHandler.END
