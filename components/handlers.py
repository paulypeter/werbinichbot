""" conversation handlers """

from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

from .misc_commands import cancel
from .character import (
    set_character,
    choose_player,
    choose_player_to_set_solved,
    set_character_solved
)
from .user import select_user_to_delete, delete_user, set_user_pw, enter_user_pw
from .game import (
    start,
    join_game,
    set_own_name,
    set_game_id,
    set_game_pw,
    enter_game_pw,
    cancel_join_game
)
from .constants import (
    SETTING_GAME_ID,
    SETTING_GAME_PW,
    ENTERING_GAME_PW,
    SETTING_OWN_NAME,
    SETTING_CHARACTER,
    DELETE_USER,
    ENTER_USER_PW,
    SETTING_CHARACTER_SOLVED
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
    fallbacks=[CommandHandler('abbrechen', cancel_join_game)],
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

set_pw_handler = ConversationHandler(
    entry_points = [CommandHandler('pw_setzen', set_user_pw)],
    states = {
        ENTER_USER_PW: [MessageHandler(Filters.text & ~Filters.command, enter_user_pw)],
    },
    fallbacks=[CommandHandler('abbrechen', cancel)],
)

set_solved_handler = ConversationHandler(
    entry_points = [CommandHandler('geloest_setzen', choose_player_to_set_solved)],
    states = {
        SETTING_CHARACTER_SOLVED: [CallbackQueryHandler(set_character_solved)],
    },
    fallbacks=[CommandHandler('abbrechen', cancel)],
)
