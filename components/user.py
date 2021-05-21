""" User methods """
import string
import random

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext
from passlib.hash import pbkdf2_sha256 as sha256

from .misc_commands import r
from .constants import ADMIN, DELETE_USER, ENTER_USER_PW
from .game import leave_game

def select_user_to_delete(update: Update, _: CallbackContext) -> int:
    """ select user """
    if str(update.message.from_user.id) != ADMIN:
        return ConversationHandler.END
    keys = r.scan(0)[1]
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

def set_delete_user_data(update: Update, _: CallbackContext) -> int:
    user_id = update.message.from_user.id
    r.delete(user_id)
    message = "Deine Daten werden komplett gelöscht."
    update.message.reply_text(message)
    return ConversationHandler.END

def set_user_pw(update: Update, _: CallbackContext) -> int:
    user_id = update.message.from_user.id
    pw = generate_random_pw(8)
    pw_hash = sha256.hash(pw)
    r.hset(user_id, "pw_hash", pw_hash)
    r.hset(user_id, "change_pw", "true")
    update.message.reply_text(
        f'Dein Passwort ist: {pw}\nBitte ändere es bei der Anmeldung!'
        f'\n\nDein Nutzername ist {user_id} .')
    return ConversationHandler.END

def enter_user_pw(update: Update, _: CallbackContext) -> int:
    user_id = update.message.from_user.id
    user_pw = update.message.text
    if user_pw in ["None", ""]:
        message = "Bitte gib ein anderes Passwort ein."
        res =  ENTER_USER_PW
    else:
        pw_hash = sha256.hash(user_pw)
        r.hset(user_id, "pw_hash", pw_hash)
        message = f'Passwort gesetzt.\nDein Nutzername ist {user_id}.'
        res = ConversationHandler.END
    update.message.reply_text(message)
    return res

def generate_random_pw(size):
    chars = string.digits + string.ascii_letters
    res = ""
    for _ in range(size):
        res += random.choice(chars)
    return res
