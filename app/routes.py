import os
import logging
from flask import request, abort, render_template
from .settings import Settings
from . import transactions
from . import actions
from . import utils

_LOGGER = logging.getLogger('API')
_LOGGER.setLevel(logging.INFO)

APP_ROOT = os.environ.get("HIGHSCORE_APP_ROOT", "")
MAX_HIGHSCORES = int(os.environ.get("HIGHSCORE_MAX_COUNT", 100))
DEFAULT_HIGHSCORES = int(os.environ.get("DEFAULT_HIGHSCORES", 20))


def add_endpoins(app):

    @app.route("{}".format(APP_ROOT if APP_ROOT else "/"))
    def api_about():
        settings = Settings()
        services = [
            {"url": "{}/{}".format(APP_ROOT, k), "description": v}
            for k, v in settings.discover_active_services().items()
        ]
        return render_template("about.html", services=services)

    @app.route(
        "{}/highscore".format(APP_ROOT),
        methods=["GET"],
    )
    def api_highscore_games():
        settings = Settings()
        games = [
            {
                "url": "{}/highscore/{}".format(APP_ROOT, k),
                "description": settings.get_game_name(k)
            }
            for k in settings.get_games_that_uses('scores')
            if settings.has_game(k)
        ]
        return render_template("service.html", name="Highscores", games=games)

    @app.route(
        "{}/highscore/<game>/<score_type>".format(APP_ROOT),
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
            if actions.is_valid_request(settings, game, score_type, req):
                ranked_entry = transactions.update_highscore(
                    settings, game, score_type, req,
                )
                game_settings = settings.get_game_settings(game)
                if (game_settings['type'] == 'raw'):
                    return utils.scores_to_raw(
                        ranked_entry, game_settings['delimiter'],
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
        "{}/highscore/<game>/<score_type>".format(APP_ROOT), methods=["GET"],
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
        count = min(
            int(request.args.get(
                'count',
                game_settings.get('scoresToList', DEFAULT_HIGHSCORES),
            )),
            MAX_HIGHSCORES,
        )
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
        "{}/highscore/<game>".format(APP_ROOT), methods=["GET"],
    )
    def api_get_scores_page(game):
        settings = Settings()
        if not settings.has_game(game):
            abort(404)
        scores = settings.get_game_scores(game)
        name = settings.get_game_name(game)
        game_settings = settings.get_game_settings(game)
        count = min(
            int(request.args.get(
                'count',
                game_settings.get('scoresToList', DEFAULT_HIGHSCORES),
            )),
            MAX_HIGHSCORES,
        )
        all_highscores = {}
        score_types = list(scores.keys())
        for score_type in score_types:
            score_settings = settings.get_score_settings(game, score_type)
            _, highscores = transactions.get_highscores(
                game, score_type, score_settings['score'],
            )
            ranked_highscores = actions.get_sorted_ranked_scores(
                highscores, score_settings["sort"],
            )
            scores[score_type].update(
                count=len(ranked_highscores),
                type=score_type,
                name=score_settings.get('name', score_type.capitalize()),
                score_name=score_settings.get("scoreName", "Score"),
            )
            all_highscores[score_type] = ranked_highscores[:count]

        return render_template(
            'highscores.html',
            scores=scores,
            name=name,
            all_highscores=all_highscores,
        )

    @app.route(
        "{}/messages/<game>/<message_type>".format(APP_ROOT), methods=["GET"]
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
