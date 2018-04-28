import os
import logging

SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings', 'settings.json')

_LOGGER = logging.getLogger('SETTINGS')
_LOGGER.setLevel(logging.INFO)
_LOGGER.info("Settings in: {}".format(SETTINGS_PATH))

def _settings():
    try:
        with open(SETTINGS_PATH) as fh:
            settings = json.load(fh)
    except:
        settings = {}
        _LOGGER.warning("No settings means server will refuse everything")

    return settings

def has_game_scores(game, score_type):
    game_settings =_settings().get('games', {}).get(game, False)
    if not game_settings:
        return False
    if not game_settings.get('scores', {}).get(score_type, False):
        return False
    return True


def get_game_settings(game):
    game_settings =_settings().get('games', {}).get('settings', {
        "type": "raw",
        "delimiter": "\t",
	"line": "\n",
    })
    return game_settings


def get_score_settings(game, score_type):
    def _get_sort(s):
        if s == "ascending":
            return -1
        elif s == "descending":
            return 1
        elif isinstance(s, str):
            return 0
        else:
            return s

    def _get_type(s):
        if s == "int":
            return int
        elif s == "float":
            return float
        elif isinstance(s, str):
            return str
        else:
            return s

    game_settings =_settings().get('games', {}).get(game, {}).get('scores', {})
    if score_type not in game_settings:
        _LOGGER.error("{} not in {}".format(score_type, _settings()))
    score_settings = game_settings.get(score_type, {
	"sort": "ascending",
	"score": "int",
    })
    score_settings["sort"] = _get_sort(score_settings["sort"])
    score_settings["score"] = _get_type(score_settings["score"])
    return score_settings
