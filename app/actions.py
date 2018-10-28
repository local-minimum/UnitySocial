#!/usr/bin/env python3
import os
import hashlib
from functools import cmp_to_key


def _get_secret():
    return os.environ.get("HIGHSCORE_SECRET", "RatatosK")


def _get_concatenated_request(req, reqtype):
    if reqtype == "highscore":
        if "name" not in req or "score" not in req:
            return ""
        return "{}{}{}".format(
            req.get("name", ""),
            req.get("score", ""),
            _get_secret(),
        )
    elif reqtype == "message":
        if "message" not in req:
            return ""
        return "{}{}".format(req.get("message"), _get_secret())
    else:
        return ""


def _get_checksum(req, reqtype):
    return hashlib.md5(
        _get_concatenated_request(req, reqtype).encode('utf8'),
    ).hexdigest()


def is_valid_request(req, reqtype):
    return req.get("checkSum", '--invalid--').lower() == _get_checksum(
        req, reqtype,
    )


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


def get_sorted_scores(highscores, sort_cmp):
    return sorted(
        highscores,
        key=cmp_to_key(lambda a, b: sort_cmp * (a["score"] - b["score"])),
    )


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
