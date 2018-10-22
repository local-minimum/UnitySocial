#! /bin/env python3
import logging
import os

from flask import Flask

from app import api, pages

_LOGGER = logging.getLogger('app')
_LOGGER.setLevel(logging.INFO)


def create_app():
    approot = os.environ.get("HIGHSCORE_APP_ROOT", "")
    app = Flask("HighScores")
    api.add_endpoins(app, approot)
    pages.add_endpoins(app, approot)
    return app


if __name__ == "__main__":
    _LOGGER.info("Starting app")
    app = create_app()
    app.run(host="0.0.0.0")
    _LOGGER.info("Stopping app")
