""" conversation handlers """

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

from .misc_commands import cancel
from .character import set_character, choose_player
from .delete_user import select_user_to_delete, delete_user
from .game import (
    start,
    join_game,
    set_own_name,
    set_game_id,
    set_game_pw,
    enter_game_pw
)
from .constants import (
    SETTING_GAME_ID,
    SETTING_GAME_PW,
    ENTERING_GAME_PW,
    SETTING_OWN_NAME,
    SETTING_CHARACTER,
    DELETE_USER
)

set_own_name_handler = ConversationHandler(
    entry_points = [CommandHandler('start', start)],
    states = {
        SETTING_OWN_NAME: [MessageHandler(Filters.text & ~Filters.command, set_own_name)],
    },
    fallbacks=[CommandHandler('abbrechen', cancel)],
)

join_game_handler = ConversationHandler(
    entry_points = [CommandHandler('spiel_beitreten', join_game)],
    states = {
        SETTING_GAME_ID: [MessageHandler(Filters.text & ~Filters.command, set_game_id)],
        SETTING_GAME_PW: [MessageHandler(Filters.text & ~Filters.command, set_game_pw)],
        ENTERING_GAME_PW: [MessageHandler(Filters.text & ~Filters.command, enter_game_pw)],
    },
    fallbacks=[CommandHandler('abbrechen', cancel)],
)

set_character_handler = ConversationHandler(
    entry_points = [CommandHandler('charakter_eingeben', choose_player)],
    states = {
        SETTING_CHARACTER: [MessageHandler(Filters.text & ~Filters.command, set_character)]
    },
    fallbacks=[CommandHandler('abbrechen', cancel)],
)

delete_user_handler = ConversationHandler(
    entry_points = [CommandHandler('select_user_to_delete', select_user_to_delete)],
    states = {
        DELETE_USER: [CallbackQueryHandler(delete_user)],
    },
    fallbacks=[CommandHandler('abbrechen', cancel)],
)
