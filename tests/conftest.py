import pytest
import json
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
