#!/usr/bin/env python
# pylint: disable=C0116
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.

Redis:
    {
    "u_id1": {"name": NAME, "character": CHARACTER, "game_id": GAME_ID, ["game_host": "true", "game_pw": GAME_PW]},
    "u_id2": {"name": NAME, "character": CHARACTER, "game_id": GAME_ID},
    "u_id3": {"name": NAME, "character": CHARACTER, "game_id": GAME_ID},
    ...
    }
"""

import logging
import regex

from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
    CallbackQueryHandler
)

from components.character import list_player_chars
from components.misc_commands import r
from components.constants import SETTING_CHARACTER
from components.game import leave_game, list_games
from components.user import set_delete_user_data
from components.handlers import (
    set_own_name_handler,
    join_game_handler,
    set_character_handler,
    delete_user_handler,
    set_pw_handler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

def is_valid_input(user_input):
    match = regex.match(r'[0-9äöüÄÖÜßa-zA-Z\-\. ]*\Z', user_input)
    return match is not None

def button_clicked(update: Update, _: CallbackContext) -> int:
    query = update.callback_query
    query.answer()
    r.hset(query.from_user.id, "selected_player", query.data)
    query.edit_message_text(text = f'Charakter für {r.hget(query.data, "name")} eingeben:')
    return SETTING_CHARACTER

def main() -> None:
    # Create the Updater and pass it your bot's token.
    f = open("token.txt", "r")
    token = f.read().strip()
    updater = Updater(token)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("charaktere_anzeigen", list_player_chars))
    dispatcher.add_handler(CommandHandler("spiel_verlassen", leave_game))
    dispatcher.add_handler(CommandHandler("spiele_anzeigen", list_games))
    dispatcher.add_handler(CommandHandler("daten_loeschen", set_delete_user_data))
    dispatcher.add_handler(delete_user_handler)
    dispatcher.add_handler(set_own_name_handler)
    dispatcher.add_handler(set_character_handler)
    dispatcher.add_handler(set_pw_handler)

    dispatcher.add_handler(join_game_handler)

    updater.dispatcher.add_handler(CallbackQueryHandler(button_clicked))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
