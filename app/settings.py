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

    def _get_game(self, game):
        return self._settings.get('games', {}).get(game, {})

    def get_game_name(self, game):
        return self._get_game(game).get('name', game.capitalize())

    def get_game_scores(self, game):
        game_settings = self._get_game(game)
        if not game_settings:
            _LOGGER.warning("Game {} not in settings".format(game))
            return {}
        return game_settings.get('scores', {})

    def has_game_scores(self, game, score_type):
        game_settings = self._get_game(game)
        if not game_settings:
            return False
        if not game_settings.get('scores', {}).get(score_type, False):
            return False
        return True

    def get_game_settings(self, game):
        ret = {}
        ret.setdefault("type", "raw")
        ret.setdefault("delimiter", "\t")
        ret.setdefault("line", '\n')
        ret.setdefault("discoverability", 'listed')
        game_settings = (
            self._get_game(game).get('settings', ret)
        )
        ret.update(game_settings)
        return ret

    @staticmethod
    def _is_listed(game):
        return (
            game
            .get('settings', {})
            .get('discoverability', 'listed') == 'listed'
        )

    def discover_active_services(self):
        def game_setting_2_service(game):
            ret = []
            if 'scores' in game and self._is_listed(game):
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

    def get_games_that_uses(self, service):
        def has_service(game):
            return self._is_listed(game) and service in game

        assert service in ['scores']
        games = set(
            k for k, v in self._settings.get('games', {}).items()
            if has_service(v)
        )
        return sorted(games)

    def get_score_settings(self, game, score_type):
        def _sorter(s):
            if s == "ascending":
                return -1
            elif s == "descending":
                return 1
            elif isinstance(s, str):
                return 0
            else:
                return s

        def _converter(s):
            if s == "int":
                return int
            elif s == "float":
                return float
            elif isinstance(s, str):
                return str
            else:
                return s

        if not self.has_game_scores(game, score_type):
            _LOGGER.error("{} not known to {}".format(score_type, game))
        game_settings = self.get_game_scores(game)
        ret = {}
        ret.setdefault('sort', 'ascending')
        ret.setdefault('score', 'int')
        score_settings = game_settings.get(score_type, ret)
        ret.update(score_settings)
        ret["sort"] = _sorter(score_settings["sort"])
        ret["score"] = _converter(score_settings["score"])
        return ret

    def get_message_settings(self game, message_type):
        return sort, maxlen
