import json
import logging
import os
from functools import cmp_to_key
import datetime as dt

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


MESSAGES_PATTERN = os.path.join(os.path.dirname(__file__), 'db', '{}.messages')
"""
{
    "msg": str
    "star": int
    "created": datestr
    "modified": datestr
}
"""


def get_messages(game, message_type, sort):
    try:
        with open(MESSAGES_PATTERN.format(game)) as fh:
            all_messages = json.load(fh)
    except FileNotFoundError:
        all_messages = {}

    return all_messages, sorted(
        all_messages.get(message_type, []), key=cmp_to_key(sort)
    )


def add_message(settings, game, message_type, req):
    sort, maxlen = settings.get_message_settings(game, message_type)
    all_messages, messages = get_messages(game, message_type, sort)
    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    mmxid = max(e['id'] for e in messages) if messages else 0
    entry = {
        "msg": req['msg'],
        "star": 0,
        "created": now,
        "modified": now,
        "id": maxid + 1,
    }
    messages = messages[:maxlen - 1]
    messages.append(entry)
    messages = sorted(messages, key=cmp_to_key(sort))
    all_messages[message_type] = messages
    with open(MESSAGES_PATTERN.format(game), 'w') as fh:
        json.dump(all_messages, fh)
    return messages


def star_by_id(settings, game, message_type, req):
    msgid = int(req['id'])
    with open(MESSAGES_PATTERN.format(game)) as fh:
        all_messages = json.load(fh)
    except FileNotFoundError:
        all_messages = {}

    messages = all_messages.get(message_type, [])
    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    for idx, e in enumerate(messages):
        if e['id'] == msgid:
            e["star"] += 1
            e["modified"] = now
            messages[idx] = e
            break
    all_messages[message_type] = messages
    with open(MESSAGES_PATTERN.format(game), 'w') as fh:
        json.dump(all_messages, fh)
