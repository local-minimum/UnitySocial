import json
import logging
import os

from flask import abort

from . import actions


_LOGGER = logging.getLogger('TRANSACTIONS')
_LOGGER.setLevel(logging.INFO)

HIGHSCORES_PATTERN = os.path.join(os.path.dirname(__file__), 'db', '{}.json')


def get_highscores(game, score_type, dtype):
    try:
        with open(HIGHSCORES_PATTERN.format(game)) as fh:
            all_highscores = json.load(fh)
    except FileNotFoundError:
        all_highscores = {}
    highscores = [
        {**e, **{'score': dtype(e['score'])}}
        for e in all_highscores.get(score_type, [])
    ]
    return all_highscores, highscores


def update_highscore(settings, game, score_type, req):
    score_settings = settings.get_score_settings(game, score_type)
    all_highscores, highscores = get_highscores(
        game, score_type, score_settings['score'],
    )
    try:
        entry = {
            "name": req["name"],
            "score": score_settings["score"](req["score"])
        }
    except ValueError:
        _LOGGER.error("settings {} req {}".format(score_settings, req))
        abort(403)
    highscores.append(entry)

    all_highscores[score_type] = highscores
    with open(HIGHSCORES_PATTERN.format(game), 'w') as fh:
        json.dump(all_highscores, fh)
    scores = actions.get_sorted_scores(highscores, score_settings["sort"])
    entry.update(rank=actions.get_entry_rank(scores, entry))
    return entry
