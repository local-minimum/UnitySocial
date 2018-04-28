#! /bin/env python3
import logging

from flask import Flask

from . import api

_LOGGER = logging.get_LOGGER('app')
_LOGGER.setLevel(logging.INFO)


def create_app():
    app = Flask("HighScores")
    api.add_api(app)
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0")
