#! /bin/env python3
import os
import hashlib
import json
from functools import cmp_to_key

from flask import Flask, request, abort

try:
    with open(os.path.join(os.path.dirname(__file__, 'settings', 'settings.json')) as fh:            
        settings = json.load(fh))
except:
    settings = {}

app = Flask("HighScores")

MD5 = hashlib.md5()

HIGHSCORES_PATTERN = os.path.join(os.path.dirname(__file__, 'db', '{}.json'))

def get_highscore(game, score_type):
    try:
        with open(HIGHSCORES_PATTERN.format(game)) as fh:
            all_highscores = json.parse(fh)
    except:
        all_highscores = {}
    return all_highscores, all_highscores.get(score_type, [])

def update_highscore(game, score_type, req):
    all_highscores, highscore = get_highscore(game, score_type)
    score_settings = get_score_settings(game, score_type)    
    entry = {
        "name": req["name"],
        "score": score_settings["score"](req["score"])
    }
    highscores.append(entry)

    all_highscores[score_type] = highscores
    with open(HIGHSCORES_PATTERN.format(game), 'w') as fh:
        json.dump(all_highscores, fh)
    scores = get_sorted_scores(highscores, score_settings["sort"])
    entry.update(rank=scores.index(entry) + 1)
    return entry
    
def get_sorted_scores(highscores, sort_cmp):
    return sorted(highscores, key=cmp_to_key(lambda a, b: sort_cmp * (a["score"] - b["score"])))

def get_sorted_ranked_scores(highscores, sort_cmp):
    return [{'rank': i + 1} + entry for i, entry in enumerate(get_sorted_scores(highscores, sort_cmp))]


def get_secret():
    return os.environ.get("HIGHSCORE_SECRET", "RatatosK")


def get_concatenated_request(req):
    return "{}{}{}".format(
        req["name"],
        req["score"],
        get_secret(),
    )


def get_checksum(req):
    MD5.update(get_concatenated_request(req))
    return MD5.hexdigest()


def has_game_scores(game, score_type):
    game_settings = settings.get('games', {}).get(game, {})
    if not game_settings:
        return False
    if not game_settings.get(score_type, {}):
        return False

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
            return 1
        elif s == "descending":
            return -1
        else:
            return 0

    def _get_type(s):
        if s == "int":
            return int
        elif s == "float":
            return float
        else:
            return str

    game_settings = settings.get('games', {}).get(game, {})
    score_settings = game_settings.get(score_type, {
	"sort": "ascending",
	"score": "int",
    })
    score_settings["sort"] = _get_sort(score_settings["sort"])
    score_settings["score"] = _get_type(score_settings["score"])
    return score_settings


def is_valid_request(game, score_type, req):
    return has_game_scores(game, score_type) and req["checksum"] == get_checksum(req)


def entry_to_raw(entry, delim):
    return entry['rank'] + delim + entry['name'] + delim + entry['score']


@app.route("/highscore/<game>/<score_type>", methods=["POST"])
def post_highscore(game, score_type):
    req = request.json()
    try:
        if is_valid_request(game, score_type, req):
            ranked_entry = update_highscore(game, score_type, req)
            game_settings = get_game_settings(game)
            if (game_settings['format'] == 'raw'):
                return entry_to_score(ranked_entry, game_settings['delimiter'])
            abort(404)
        else:
            abort(403)
    except KeyError:
        abort(404)



@app.route("/highscore/<game>/<score_type>", methods=["GET"])
def get_highscore(game, score_type):
    if not has_game_scores(game, score_type):
        abort(404)
    count = 10
    _, highscores = get_highscore(game, score_type)
    scores = get_sorted_ranked_scores(highscores, score_settings["sort"])
    game_settings = get_game_settings(game)
    if (game_settings['format'] == 'raw'):
        return game_settings['line'].join([entry_to_score(entry, game_settings['delimiter']) for entry in scores])
    abort(404)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
