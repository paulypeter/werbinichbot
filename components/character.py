""" methods concerning assigned characters """
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

from .constants import SETTING_CHARACTER, SETTING_CHARACTER_SOLVED
from .misc_commands import (
    player_keyboard,
    get_other_players,
    r,
    send_select_player_message
)

def set_character(update: Update, _: CallbackContext) -> int:
    """ Set another player's char """
    selected_player = r.hget(update.message.from_user.id, "selected_player")
    chosen_character = update.message.text
    r.hset(selected_player, "character", chosen_character)
    r.hset(selected_player, "solved", "false")
    r.hdel(update.message.from_user.id, "selected_player")
    update.message.reply_text(
        f'Alles klar! Der Charakter für {r.hget(selected_player, "name")} ist {chosen_character}.')
    return ConversationHandler.END

def choose_player(update: Update, _: CallbackContext):
    """ Choose a player """
    user_id = str(update.message.from_user.id)
    keys = get_other_players(user_id, filter_players=True)
    if len(keys) == 0:
        update.message.reply_text("Es kann niemandem ein Charakter zugewiesen werden.")
        res = ConversationHandler.END
    elif r.exists(user_id) and r.hget(user_id, "game_id") != "None":
        send_select_player_message(update, filter_players=True)
        res = SETTING_CHARACTER
    else:
        update.message.reply_text("Du spielst momentan nicht. Tritt erst einem Spiel bei!")
        res = ConversationHandler.END
    return res

def list_player_chars(update: Update, _: CallbackContext):
    """ List other players and their chars in this game """
    user_id = str(update.message.from_user.id)
    if r.exists(user_id) and r.hget(user_id, "game_id") != "None":
        keys = get_other_players(user_id)
        message_text = ""
        for key in keys:
            character = r.hget(key, "character")
            solved = " ✓" if r.hget(key, "solved") == "true" else ""
            if key != str(user_id) and str(character) != "None":
                message_text += f'{r.hget(key, "name")} ist {character}{solved}\n'
        if message_text == "":
            message_text = "Es wurden noch keine Charaktere eingetragen!"
    else:
        message_text = "Du spielst momentan nicht. Tritt erst einem Spiel bei!"
    update.message.reply_text(message_text)

def choose_player_to_set_solved(update: Update, _: CallbackContext):
    """ Choose a player who solved his character """
    user_id = str(update.message.from_user.id)
    keys = get_other_players(user_id, filter_players=False)
    if len(keys) == 0:
        update.message.reply_text("Es ist niemand sonst in diesem Spiel.")
        res = ConversationHandler.END
    elif r.exists(user_id) and r.hget(user_id, "game_id") != "None":
        send_select_player_message(update, filter_players=False)
        res = SETTING_CHARACTER_SOLVED
    else:
        update.message.reply_text("Du spielst momentan nicht. Tritt erst einem Spiel bei!")
        res = ConversationHandler.END
    return res

def set_character_solved(update: Update, _: CallbackContext) -> int:
    """ set user character solved """
    query = update.callback_query
    query.answer()
    user_id_to_set_solved = query.data
    user_name_to_set_solved = r.hget(user_id_to_set_solved, "name")
    r.hset(user_id_to_set_solved, "solved", "true")
    query.edit_message_text(text=f'{user_name_to_set_solved}s Charakter wurde als gelöst markiert.')
    return ConversationHandler.END
