""" methods concerning assigned characters """
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, CallbackContext

from .constants import SETTING_CHARACTER
from .misc_commands import player_keyboard, get_other_players, r

def set_character(update: Update, _: CallbackContext) -> int:
    """ Set another player's char """
    selected_player = r.hget(update.message.from_user.id, "selected_player")
    chosen_character = update.message.text
    r.hset(selected_player, "character", chosen_character)
    r.hdel(update.message.from_user.id, "selected_player")
    update.message.reply_text(
        f'Alles klar! Der Charakter für {r.hget(selected_player, "name")} ist {chosen_character}.')
    return ConversationHandler.END

def choose_player(update: Update, _: CallbackContext):
    """ Choose a player """
    user_id = str(update.message.from_user.id)
    keys = get_other_players(user_id)
    if len(keys) == 0:
        update.message.reply_text("Warte noch, bis andere Spieler beigetreten sind.")
        res = ConversationHandler.END
    elif r.exists(user_id) and r.hget(user_id, "game_id") != "None":
        keyboard = player_keyboard(update.message.from_user.id)
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text(text='Spieler auswählen: ', reply_markup=reply_markup)
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
            if key != str(user_id) and character is not None:
                message_text += r.hget(key, "name") + " ist " + character + "\n"
        if message_text == "":
            message_text = "Es wurden noch keine Charaktere eingetragen!"
    else:
        message_text = "Du spielst momentan nicht. Tritt erst einem Spiel bei!"
    update.message.reply_text(message_text)
