import os
import logging
from flask import request, abort
import app.settings as settings
import app.actions as actions
import app.transactions as transactions

_LOGGER = logging.get_LOGGER('API')
_LOGGER.setLevel(logging.INFO)

APP_ROOT = os.environ.get("HIGHSCORE_APP_ROOT", "")


def entry_to_raw(entry, delim):
    return "{}{}{}{}{}".format(entry['rank'], delim, entry['name'], delim, entry['score'])


def add_api(app):

    @app.route(
        "{}/highscore/<game>/<score_type>".format(APP_ROOT),
        methods=["POST"],
    )
    def api_post_highscore(game, score_type):
        req = request.form
        try:
            if actions.is_valid_request(game, score_type, req):
                ranked_entry = transactions.update_highscore(
                    game, score_type, req,
                )
                game_settings = settings.get_game_settings(game)
                if (game_settings['type'] == 'raw'):
                    return entry_to_raw(
                        ranked_entry, game_settings['delimiter'],
                    )
                _LOGGER.error('Game Settings not supported')
                abort(404)
            elif not settings.has_game_scores(game, score_type):
                _LOGGER.error(
                    'Unknown Game/Score {}/{}'.format(game, score_type),
                )
                abort(404)
            else:
                _LOGGER.error("Rejected post {}".format(req))
                abort(403)
        except KeyError:
            _LOGGER.error('Request missing stuff {}'.format(req))
            abort(404)



    @app.route(
        "{}/highscore/<game>/<score_type>".format(APP_ROOT), methods=["GET"],
    )
    def api_get_highscore(game, score_type):
        if not settings.has_game_scores(game, score_type):
            _LOGGER.error('Unknown Game/Score {}/{}'.format(game, score_type))
            abort(404)
        count = 10
        score_settings = settings.get_score_settings(game, score_type)
        a, highscores = transactions.get_highscores(
            game, score_type, score_settings['score'],
        )
        scores = actions.get_sorted_ranked_scores(
            highscores, score_settings["sort"],
        )
        game_settings = settings.get_game_settings(game)
        if (game_settings['type'] == 'raw'):
            return game_settings['line'].join(
                [entry_to_raw(entry, game_settings['delimiter'])
                for entry in scores],
            )
        _LOGGER.error('Unsupported game settings')
        abort(404)