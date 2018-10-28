import logging
from flask import request, abort
from .settings import Settings
from . import transactions
from . import actions
from . import utils

_LOGGER = logging.getLogger('API')
_LOGGER.setLevel(logging.INFO)


def add_endpoins(app, approot):

    @app.route(
        "{}/highscore/<game>/<score_type>".format(approot),
        methods=["POST"],
    )
    def api_post_highscore(game, score_type):
        settings = Settings()
        if (
            not settings.has_game(game)
            or settings.has_game_scores(game, score_type)
        ):
            _LOGGER.error(
                'Unknown Game/Score {}/{}'.format(game, score_type),
            )
            abort(404)

        req = request.form
        try:
            if actions.is_valid_request(req, 'highscore'):
                scores = transactions.update_highscore(
                    settings, game, score_type, req,
                )
                game_settings = settings.get_game_settings(game)
                if (game_settings['type'] == 'raw'):
                    return utils.serialize(
                        game_settings, scores, utils.scores_to_raw,
                    )
                _LOGGER.error('Game Settings not supported')
                abort(404)
            else:
                _LOGGER.error("Rejected post {}".format(req))
                abort(403)
        except KeyError:
            _LOGGER.error('Request missing stuff {}'.format(req))
            abort(404)

    @app.route(
        "{}/highscore/<game>/<score_type>".format(approot), methods=["GET"],
    )
    def api_get_highscore(game, score_type):
        settings = Settings()
        if (
            not settings.has_game(game)
            or not settings.has_game_scores(game, score_type)
        ):
            _LOGGER.error('Unknown Game/Score {}/{}'.format(game, score_type))
            abort(404)
        game_settings = settings.get_game_settings(game)
        count = utils.clip_highscore_count(request, game_settings)
        score_settings = settings.get_score_settings(game, score_type)
        _, highscores = transactions.get_highscores(
            game, score_type, score_settings['score'],
        )
        scores = actions.get_sorted_ranked_scores(
            highscores, score_settings["sort"],
        )
        return utils.serialize(
            game_settings, scores[:count], utils.scores_to_raw,
        )

    @app.route(
        "{}/messages/<game>/<message_type>".format(approot), methods=["GET"]
    )
    def api_get_messages(game, message_type):
        settings = Settings()
        if (
            not settings.has_game(game)
            or not settings.has_messages(game, message_type)
        ):
            _LOGGER.error("Unknown Game/Messages {}/{}".format(
                game, message_type,
            ))
            abort(404)
        sort, maxlen = settings.get_message_settings(game, message_type)
        _, messages = transactions.get_messages(game, message_type, sort)
        game_settings = settings.get_game_settings(game)
        return utils.serialize(
            game_settings, messages[:maxlen], utils.message_to_raw,
        )

    @app.route(
        "{}/messages/<game>/<message_type>".format(approot),
        methods=["POST"],
    )
    def api_post_messages(game, message_type):
        settings = Settings()
        if (
            not settings.has_game(game)
            or settings.has_messages(game, message_type)
        ):
            _LOGGER.error(
                'Unknown Game/Message {}/{}'.format(game, message_type),
            )
            abort(404)

        req = request.form
        try:
            if actions.is_valid_request(req, 'message'):
                game_settings = settings.get_game_settings(game)
                messages = transactions.add_message(
                    settings, game, message_type, req
                )
                if (game_settings['type'] == 'raw'):
                    return utils.raw_serializer(
                        game_settings, messages, utils.message_to_raw
                    )
                _LOGGER.error('Game Settings not supported')
                abort(404)
            else:
                _LOGGER.error("Rejected post {}".format(req))
                abort(403)
        except KeyError:
            _LOGGER.error('Request missing stuff {}'.format(req))
            abort(404)
