import os
import logging
import json
from itertools import chain
from json.decoder import JSONDecodeError

SETTINGS_PATH = os.path.join(
    os.path.dirname(__file__), 'settings', 'settings.json',
)

_LOGGER = logging.getLogger('SETTINGS')
_LOGGER.setLevel(logging.INFO)
_LOGGER.info("Settings in: {}".format(SETTINGS_PATH))


class Settings:
    def __init__(self, source=SETTINGS_PATH):
        self._settings = self._load(source)

    def _load(self, source):
        try:
            if isinstance(source, str):
                with open(SETTINGS_PATH) as fh:
                    settings = json.load(fh)
            else:
                settings = json.load(source)
        except FileNotFoundError:
            settings = {}
            _LOGGER.error(
                "Could not locate file {}. ".format(SETTINGS_PATH)
            )
        except JSONDecodeError:
            settings = {}
            _LOGGER.error(
                "Settings file is corrupt, please run through json validator",
            )
        return settings

    def get_game_name(self, game):
        return (
            self._settings
            .get('games', {})
            .get(game, {})
            .get('name', game.capitalize())
        )

    def get_game_scores(self, game):
        game_settings = self._settings.get('games', {}).get(game, False)
        if not game_settings:
            _LOGGER.warning("Game {} not in settings".format(game))
            return {}
        return game_settings.get('scores', {})

    def has_game_scores(self, game, score_type):
        game_settings = self._settings.get('games', {}).get(game, False)
        if not game_settings:
            return False
        if not game_settings.get('scores', {}).get(score_type, False):
            return False
        return True

    def get_game_settings(self, game):
        game_settings = self._settings.get('games', {}).get('settings', {
            "type": "raw",
            "delimiter": "\t",
            "line": "\n",
        })
        return game_settings

    def discover_active_services(self):
        def game_setting_2_service(game):
            ret = []
            if 'scores' in game:
                ret.append('highscore')
            return ret

        all_services = {'highscore': '(Multiple) Highscores for games'}
        game_settings = set(
            chain(*(
                game_setting_2_service(game)
                for game in self._settings.get('games', {}).values()
            ))
        )
        return {k: v for k, v in all_services.items() if k in game_settings}

    def get_score_settings(self, game, score_type):
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

        game_settings = self._settings.get(
            'games', {}).get(game, {}).get('scores', {})
        if score_type not in game_settings:
            _LOGGER.error("{} not in {}".format(score_type, self._settings))
        score_settings = game_settings.get(score_type, {
            "sort": "ascending",
            "score": "int",
        })
        score_settings["sort"] = _get_sort(score_settings["sort"])
        score_settings["score"] = _get_type(score_settings["score"])
        return score_settings
