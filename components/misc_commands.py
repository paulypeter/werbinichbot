""" Misc """
from math import ceil
import redis

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

def cancel(update: Update, _: CallbackContext) -> int:
    """ cancel an action """
    reply_markup = InlineKeyboardMarkup([[]])
    update.message.reply_text(
        'Aktion abgebrochen.', reply_markup=reply_markup
    )
    return ConversationHandler.END

def get_other_players(user_id):
    """ get other players in the same game """
    keys = r.keys(pattern="*")
    player_list = []
    user_game_id = r.hget(user_id, "game_id")
    for key in keys:
        if r.hget(key, "game_id") == str(user_game_id) and str(user_id) != key:
            player_list.append(key)
    return player_list

def player_keyboard(user_id):
    """ generate a keyboard """
    def get_number_of_rows(player_list):
        num_of_players = len(player_list)
        if num_of_players % 2 == 0:
            res = int(num_of_players / 2)
        else:
            res = ceil(num_of_players / 2)
        return res

    def player_button(user_id):
        name = r.hget(user_id, "name")
        return InlineKeyboardButton(name, callback_data=user_id)

    keyboard = []
    player_index = 0
    keys = get_other_players(user_id)
    num_of_rows = get_number_of_rows(keys)
    for _ in range(num_of_rows):
        button_row = []
        for _ in range(2):
            if player_index < len(keys) and user_id != keys[player_index]:
                button_row.append(player_button(keys[player_index]))
            player_index += 1
        keyboard.append(button_row)
    return keyboard

r = redis.StrictRedis(decode_responses=True, db=2)
