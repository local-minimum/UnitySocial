from flask import request, abort, render_template

from .settings import Settings
from . import transactions
from . import actions
from . import utils


def add_endpoins(app, approot):

    @app.route("{}".format(approot if approot else "/"))
    def about():
        settings = Settings()
        services = [
            {"url": "{}/{}".format(approot, k), "description": v}
            for k, v in settings.discover_active_services().items()
        ]
        return render_template("about.html", services=services)

    @app.route(
        "{}/highscore".format(approot),
        methods=["GET"],
    )
    def highscore_games():
        settings = Settings()
        games = [
            {
                "url": "{}/highscore/{}".format(approot, k),
                "description": settings.get_game_name(k),
            }
            for k in settings.get_games_that_uses('scores')
            if settings.has_game(k)
        ]
        return render_template("service.html", name="Highscores", games=games)

    @app.route(
        "{}/messages".format(approot),
        methods=["GET"],
    )
    def messages_games():
        settings = Settings()
        games = [
            {
                "url": "{}/messages/{}".format(approot, k),
                "description": settings.get_game_name(k),
            }
            for k in settings.get_games_that_uses('messages')
            if settings.has_game(k)
        ]
        return render_template("service.html", name="Messages", games=games)

    @app.route(
        "{}/highscore/<game>".format(approot), methods=["GET"],
    )
    def highscores_page(game):
        settings = Settings()
        if not settings.has_game(game):
            abort(404)
        scores = settings.get_game_scores(game)
        name = settings.get_game_name(game)
        game_settings = settings.get_game_settings(game)
        count = utils.clip_highscore_count(request, game_settings)
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
