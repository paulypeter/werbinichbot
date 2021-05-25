""" Methods and handlers relating to the game """
from telegram import Update
from telegram.ext import ConversationHandler, CallbackContext
from passlib.hash import pbkdf2_sha256 as sha256

from .misc_commands import r
from .constants import (
    SETTING_OWN_NAME,
    SETTING_GAME_ID,
    SETTING_GAME_PW,
    ENTERING_GAME_PW,
    ADMIN
)

def start(update: Update, _: CallbackContext) -> int:
    """ Start the bot """
    update.message.reply_text('Hallo! Bitte gib deinen Namen ein.')
    return SETTING_OWN_NAME

def set_own_name(update: Update, context: CallbackContext):
    """ Setting your own name """
    r.hset(update.message.from_user.id, "name", update.message.text.strip())
    r.hset(update.message.from_user.id, "game_id", "None")
    update.message.reply_text(f'Danke, {update.message.text.strip()}. Viel Spaß!')
    message = f'{update.message.text.strip()} hat sich gerade angemeldet!'
    context.bot.send_message(chat_id=ADMIN, text=message)
    return ConversationHandler.END

def join_game(update: Update, _: CallbackContext) -> int:
    """ Join a game """
    user_id = str(update.message.from_user.id)
    if not r.exists(user_id):
        update.message.reply_text('Bitte trage erst mit /start einen Namen für Dich ein!')
        return ConversationHandler.END
    update.message.reply_text('Bitte gib die Spiel-ID ein.')
    return SETTING_GAME_ID

def leave_game(update: Update, _: CallbackContext) -> int:
    """ leave current game """
    user_id = str(update.message.from_user.id)
    if r.exists(user_id):
        game_id = r.hget(user_id, "game_id")
        if game_id == "None":
            message = "Du spielst momentan nicht."
        else:
            r.hset(user_id, "game_id", "None")
            r.hdel(user_id, "character", "game_host")
            message = f"Du hast das Spiel {game_id} verlassen!"
    else:
        message = "Du spielst momentan nicht."
    update.message.reply_text(message)

def set_game_id(update: Update, _: CallbackContext) -> int:
    """ enter a game id to create or join """
    game_id = update.message.text.strip()
    user_id = update.message.from_user.id
    games_list = get_list_of_games()
    if game_id == "None":
        message = "Bitte eine andere ID eingeben:"
        res = SETTING_GAME_ID
    elif game_id in games_list:
        # join game, delete game_id if password is wrong
        r.hset(user_id, "game_id", game_id)
        message = "Spiel gefunden. Bitte gib das Passwort ein:"
        res = ENTERING_GAME_PW
    else:
        # create new game
        r.hset(user_id, "game_id", game_id)
        r.hset(user_id, "game_host", "true")
        message = "Neues Spiel. Bitte setze ein Passwort:"
        res = SETTING_GAME_PW
    update.message.reply_text(message)
    return res

def get_game_pw(game_id):
    """ get game pw from host """
    keys = r.scan(0)[1]
    res = "None"
    for key in keys:
        if r.hexists(key, "game_host") and r.hget(key, "game_id") == game_id:
            res = str(r.hget(key, "game_pw"))
    return res

def set_game_pw(update: Update, _: CallbackContext) -> int:
    """ set a game PW """
    user_id = update.message.from_user.id
    game_pw = update.message.text.strip()
    if game_pw in ["None", ""]:
        message = "Bitte gib ein anderes Passwort ein."
        res =  SETTING_GAME_PW
    else:
        pw_hash = sha256.hash(game_pw)
        r.hset(user_id, "game_pw", pw_hash)
        message = 'Passwort gesetzt.'
        res = ConversationHandler.END
    update.message.reply_text(message)
    return res

def enter_game_pw(update: Update, _: CallbackContext) -> int:
    """ enter a pw for the chosen game """
    user_id = update.message.from_user.id
    game_id = r.hget(user_id, "game_id")
    entered_pw = update.message.text.strip()
    pw_hash = get_game_pw(game_id)
    if sha256.verify(entered_pw, pw_hash):
        # entered correct password
        message_text = "Du bist dem Spiel beigetreten!"
        res = ConversationHandler.END
    else:
        # wrong password
        message_text = "Falsches Passwort.\nBitte das richtige Passwort eingeben oder /abbrechen."
        res = ENTERING_GAME_PW
    update.message.reply_text(message_text)
    return res

def get_list_of_games():
    """ get a `set` of game IDs """
    keys = r.scan(0)[1]
    games_list = []
    if keys:
        for key in keys:
            game_id = r.hget(key, "game_id") or "None"
            if not game_id in games_list and game_id != "None":
                games_list.append(game_id)
    return games_list

def list_games(update: Update, _: CallbackContext) -> int:
    """ get a list of games """
    games_list = get_list_of_games()
    message = ""
    if games_list:
        for game in games_list:
            message += game + "\n"
    else:
        message = "Es sind keine Spiele eingetragen."
    update.message.reply_text(message)

def cancel_join_game(update: Update, _: CallbackContext) -> int:
    """ cancel an action """
    user_id = update.message.from_user.id
    r.hset(user_id, "game_id", "None")
    r.hdel(user_id, "game_host", "game_pw")
    update.message.reply_text(
        'Aktion abgebrochen.'
    )
    return ConversationHandler.END
