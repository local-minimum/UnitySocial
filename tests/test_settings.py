import pytest
from io import StringIO
import json

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
            }
        }
    }, settings)
    settings.flush()
    settings.seek(0)
    return app.settings.Settings(settings)


def test_discover_active_services_if_no_games(empty_settings):
    assert empty_settings.discover_active_services() == {}


def test_discover_active_services_if_games(game_settings):
    assert (
        set(game_settings.discover_active_services().keys()) == {'highscore'}
    )


@pytest.mark.parametrize('game,name', (
    ('debug', 'Debug'),
    ('debug2', 'Crazy'),
))
def test_get_game_name(game_settings, game, name):
    assert game_settings.get_game_name(game) == name


def test_get_unknown_game_gives_empty_scores_settings(game_settings):
    assert game_settings.get_game_scores('unknown') == {}


def test_get_game_scores(game_settings):
    assert game_settings.get_game_scores('debug') == {
        'test': {
            'sort': 'ascending',
            'score': 'int',
        }
    }
