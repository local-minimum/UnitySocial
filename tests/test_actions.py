import hashlib

import pytest

import app.actions


@pytest.mark.parametrize("name,score,hashname,hashscore,expect", (
    ('debug', 'test', 'debug', 'test', True),
    ('debug', 'test', 'medd', 'test', False),
    ('debug', 'test', 'debug', '233', False),
    ('debug', 'test', 'mesaf', '233', False),
))
def test_is_valid_highscore_request(name, score, hashname, hashscore, expect):
    req = {
        'name': name,
        'score': score,
        'checkSum': hashlib.md5(
            "{}{}RatatosK".format(hashname, hashscore).encode('utf8')
        ).hexdigest(),
    }
    assert app.actions.is_valid_request(req, 'highscore') == expect
