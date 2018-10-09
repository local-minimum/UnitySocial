import pytest


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


@pytest.mark.parametrize("score,expect", (('test', True), ('nono', False)))
def test_has_game_scores(game_settings, score, expect):
    assert game_settings.has_game_scores("debug", score) is expect


def test_has_game_score_unknown_game(game_settings):
    assert game_settings.has_game_scores('nono', 'yesyes') is False


def test_get_game_settings(game_settings):
    assert game_settings.get_game_settings('debug') == {
        'type': 'raw',
        'delimiter': ',',
        'line': '\r\n',
        'discoverability': 'listed',
    }


def test_discover_active_services_if_no_games(empty_settings):
    assert empty_settings.discover_active_services() == {}


def test_discover_active_services_if_games(game_settings):
    assert (
        set(game_settings.discover_active_services().keys()) == {'highscore'}
    )


def test_get_score_settings(game_settings):
    settings = game_settings.get_score_settings('debug', 'test')
    assert settings['score'] == int
    assert settings['sort'] == -1


def test_get_games_that_uses(game_settings):
    assert game_settings.get_games_that_uses('scores') == ['debug', 'debug2']
