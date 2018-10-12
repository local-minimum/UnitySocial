from functools import cmp_to_key

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


@pytest.mark.parametrize("game,message_type,expect", (
    ('debug', 'test', True),
    ('debug', 'test2', True),
    ('debug', 'test4', False),
    ('debug2', 'test', False),
))
def test_has_messages(game_settings, game, message_type, expect):
    assert game_settings.has_messages(game, message_type) is expect


@pytest.mark.parametrize("message_type,idorder,maxlen", (
    ('test', [0, 2, 1], 20),
    ('test2', [1, 0, 2], None),
    ('test3', [0, 1, 2], 10),
))
def test_get_message_settings(
    game_settings, example_messages, message_type, idorder, maxlen,
):
    sort, maxln = game_settings.get_message_settings('debug', message_type)
    assert maxln == maxlen
    assert [
        e['id'] for e in sorted(example_messages, key=cmp_to_key(sort))
    ] == idorder
