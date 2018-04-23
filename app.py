#! /bin/env python3
import os
import hashlib
import json
import logging
from functools import cmp_to_key

from flask import Flask, request, abort

logger = logging.getLogger('app')
logger.setLevel(logging.INFO)

settings_path = os.path.join(os.path.dirname(__file__), 'settings', 'settings.json')
logger.info("Settings in: {}".format(settings_path))

try:
    with open(settings_path) as fh:            
        settings = json.load(fh)
except:
    settings = {}

app = Flask("HighScores")

HIGHSCORES_PATTERN = os.path.join(os.path.dirname(__file__), 'db', '{}.json')

def get_highscores(game, score_type, dtype):
    try:
        with open(HIGHSCORES_PATTERN.format(game)) as fh:
            all_highscores = json.load(fh)
    except FileNotFoundError:
        all_highscores = {}
    highscores = [{**e, **{'score': dtype(e['score'])}} for e in all_highscores.get(score_type, [])]
    logger.error("{} {} {}".format(score_type, dtype, highscores))
    return all_highscores, highscores

def update_highscore(game, score_type, req):
    score_settings = get_score_settings(game, score_type)    
    all_highscores, highscores = get_highscores(game, score_type, score_settings['score'])
    try:
        entry = {
            "name": req["name"],
            "score": score_settings["score"](req["score"])
        }
    except ValueError:
        logger.error("settings {} req {}".format(score_settings, req))
        abort(403)
    highscores.append(entry)

    all_highscores[score_type] = highscores
    with open(HIGHSCORES_PATTERN.format(game), 'w') as fh:
        json.dump(all_highscores, fh)
    scores = get_sorted_scores(highscores, score_settings["sort"])
    entry.update(rank=get_entry_rank(scores, entry))
    return entry
    
def get_sorted_scores(highscores, sort_cmp):
    return sorted(highscores, key=cmp_to_key(lambda a, b: sort_cmp * (a["score"] - b["score"])))

def get_entry_rank(scores, entry):
    val = None
    rank = 0
    count = 1
    for score in scores:
        if val is None or score['score'] != val:
            val = score['score']
            rank += count
            count = 1
        else:
            count += 1
        if score == entry:
            return rank
    return -1

def get_sorted_ranked_scores(highscores, sort_cmp):
    scores = get_sorted_scores(highscores, sort_cmp)
    val = None
    rank = 0
    count = 1
    for score in scores:
        if val is None or score['score'] != val:
            val = score['score']
            rank += count
            count = 1
        else:
            count += 1
        score.update(rank=rank)
    return scores


def get_secret():
    return os.environ.get("HIGHSCORE_SECRET", "RatatosK")


def get_concatenated_request(req):
    return "{}{}{}".format(
        req["name"],
        req["score"],
        get_secret(),
    )


def get_checksum(req):
    return hashlib.md5(get_concatenated_request(req).encode('utf8')).hexdigest()


def has_game_scores(game, score_type):
    game_settings = settings.get('games', {}).get(game, False)
    if not game_settings:
        return False
    if not game_settings.get('scores', {}).get(score_type, False):
        return False
    return True

def get_game_settings(game):
    game_settings = settings.get('games', {}).get('settings', {
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
        else:
            return 0

    def _get_type(s):
        if s == "int":
            return int
        elif s == "float":
            return float
        else:
            return s

    game_settings = settings.get('games', {}).get(game, {}).get('scores', {})
    if score_type not in game_settings:
        logger.error("{} not in {}".format(score_type, settings))
    score_settings = game_settings.get(score_type, {
	"sort": "ascending",
	"score": "int",
    })
    score_settings["sort"] = _get_sort(score_settings["sort"])
    score_settings["score"] = _get_type(score_settings["score"])
    return score_settings


def is_valid_request(game, score_type, req):
    return has_game_scores(game, score_type) and req["checkSum"].lower() == get_checksum(req)


def entry_to_raw(entry, delim):
    return "{}{}{}{}{}".format(entry['rank'], delim, entry['name'], delim, entry['score'])


@app.route("/highscore/<game>/<score_type>", methods=["POST"])
def api_post_highscore(game, score_type):
    req = request.form
    try:
        if is_valid_request(game, score_type, req):
            ranked_entry = update_highscore(game, score_type, req)
            game_settings = get_game_settings(game)
            if (game_settings['type'] == 'raw'):
                return entry_to_raw(ranked_entry, game_settings['delimiter'])
            logger.error('Game Settings not supported')
            abort(404)
        elif not has_game_scores(game, score_type):
            logger.error('Unknown Game/Score {}/{}'.format(game, score_type))
            abort(404)
        else:
            logger.error("Rejected post {}".format(req))
            abort(403)
    except KeyError:
        logger.error('Request missing stuff {}'.format(req))
        abort(404)



@app.route("/highscore/<game>/<score_type>", methods=["GET"])
def api_get_highscore(game, score_type):
    if not has_game_scores(game, score_type):
        logger.error('Unknown Game/Score {}/{}'.format(game, score_type))
        abort(404)
    count = 10
    score_settings = get_score_settings(game, score_type)
    a, highscores = get_highscores(game, score_type, score_settings['score'])
    scores = get_sorted_ranked_scores(highscores, score_settings["sort"])
    game_settings = get_game_settings(game)
    if (game_settings['type'] == 'raw'):
        return game_settings['line'].join([entry_to_raw(entry, game_settings['delimiter']) for entry in scores])
    logger.error('Unsupported game settings')
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
