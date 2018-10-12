import pytest
import json
import datetime as dt
from io import StringIO

import app.settings


@pytest.fixture
def empty_settings():
    settings = StringIO()
    return app.settings.Settings(settings)


@pytest.fixture
def game_settings():
    settings = StringIO()
    json.dump({
        'games': {
            'debug': {
                'settings': {
                    "delimiter": ",",
                    "line": '\r\n',
                },
                'scores': {
                    'test': {
                        'sort': 'ascending',
                        'score': 'int',
                    }
                },
                'messages': {
                    'test': {
                        'sort': 'star',
                        'maxLength': 20,
                    },
                    'test2': {'sort': 'modified-descending'},
                    'test3': {'maxLength': 10},
                }
            },
            'debug2': {
                'name': 'Crazy',
                'scores': {
                    'test2': {},
                }
            },
            'debug3': {
                'settings': {
                    'discoverability': 'unlisted',
                },
                'scores': {
                    'test': {},
                },
            },
            'debug4': {
                'settings': {
                    'discoverability': 'hidden',
                },
                'scores': {
                    'test': {},
                },
            }
        }
    }, settings)
    settings.flush()
    settings.seek(0)
    return app.settings.Settings(settings)


@pytest.fixture
def example_messages():
    now = dt.datetime(1999, 1, 1)
    return [
        {
            "msg": 'a',
            "star": 0,
            "created": now,
            "modified": now,
            "id": 0,
        },
        {
            "msg": 'b',
            "star": 4,
            "created": now + dt.timedelta(hours=1),
            "modified": now + dt.timedelta(hours=2),
            "id": 1,
        },
        {
            "msg": 'c',
            "star": 2,
            "created": now - dt.timedelta(hours=1),
            "modified": now - dt.timedelta(hours=2),
            "id": 2,
        },
    ]
