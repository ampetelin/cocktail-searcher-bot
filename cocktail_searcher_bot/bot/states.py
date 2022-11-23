from aiogram.fsm.state import StatesGroup, State


class SearchStates(StatesGroup):
    """Состояния FSM поиска коктейля"""
    QUERY_INPUT_STATE = State()
    COCKTAIL_DISPLAY_STATE = State()
    RECIPE_DISPLAY_STATE = State()


class FavoriteStates(StatesGroup):
    """Состояния FSM избранных коктейлей"""
    COCKTAIL_DISPLAY_STATE = State()
    RECIPE_COCKTAIL_DISPLAY_STATE = State()
