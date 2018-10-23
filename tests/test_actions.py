import hashlib

import pytest

import app.actions


@pytest.mark.parametrize("game,scorename,name,score,expect", (
    ('debug', 'test', 'me', '33', True),
    ('debug', 'test2', 'medd', '133', False),
    ('debug3', 'test', 'mesaf', '233', True),
    ('debug4', 'test', 'mesaf', '233', False),
    ('debug5', 'test', 'mesaf', '233', False),
))
def test_is_valid_request(game, scorename, name, score, expect):
    req = {
        'name': name,
        'score': score,
        'checkSum': hashlib.md5(
            "{}{}RatatosK".format(game, scorename).encode('utf8')
        ).hexdigest(),
    }
    app.actions.is_valid_request(req) == expect
