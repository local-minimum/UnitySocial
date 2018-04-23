#! /bin/env python3
import os
import hashlib

from flask import Flask, request, abort


app = Flask("HighScores")

MD5 = hashlib.md5()

HIGHSCORE = []


def update_highscore(req):
    HIGHSCORE.append(req)


def get_secret():
    return os.environ.get("HIGHSCORE_SECRET", "RatatosK")


def get_concatenated_request(req):
    return "{}{}{}{}{}".format(
        req["name"],
        req["score1"],
        req["score2"],
        req["score3"],
        get_secret(),
    )


def get_checksum(req):
    MD5.update(get_concatenated_request(req))
    return MD5.hexdigest()


def is_valid_request(req):
    return req["checksum"] == get_checksum(req)


@app.route("/highscore", methods=["POST"])
def post_highscore():
    req = request.json()
    try:
        if is_valid_request(req):
            update_highscore(req)
        else:
            abort(403)
    except KeyError:
        abort(404)


@app.route("/highscore", methods=["GET"])
def get_highscore():
    return HIGHSCORE


if __name__ == "__main__":
    app.run(host="0.0.0.0")
