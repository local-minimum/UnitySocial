import datetime as dt
from unittest.mock import patch, ANY

import pytest

import app.transactions


@patch("app.transactions.save_messages")
def test_add_messages_adds(save_messages, game_settings, example_messages):
    with patch(
        "app.transactions.get_messages",
        return_value=({'test': example_messages}, example_messages),
    ) as get_messages:
        messages = app.transactions.add_message(
            game_settings, 'debug', 'test', {'msg': 'Hello'},
        )
        get_messages.assert_called_with('debug', 'test', ANY)

    assert messages[0]['msg'] == 'Hello'
    assert messages[0]['id'] == 3
    assert messages[0]['star'] == 0


@patch("app.transactions.save_messages")
def test_star_by_id(save_messages, game_settings, example_messages):
    with patch(
        "app.transactions.get_messages",
        return_value=({'test': example_messages}, example_messages),
    ) as get_messages:
        app.transactions.star_by_id(
            game_settings, 'debug', 'test', {'id': 1},
        )
        get_messages.assert_called_with('debug', 'test', ANY)

    now = dt.datetime(1999, 1, 1)
    editdate = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M")
    save_messages.assert_called_with('debug', {'test': [
        {
            "msg": 'a',
            "star": 1,
            "created": now.strftime("%Y-%m-%dT%H:%M"),
            "modified": now.strftime("%Y-%m-%dT%H:%M"),
            "id": 0,
        },
        {
            "msg": 'c',
            "star": 2,
            "created": (now - dt.timedelta(hours=1)).strftime(
                "%Y-%m-%dT%H:%M"),
            "modified": (now - dt.timedelta(hours=2)).strftime(
                "%Y-%m-%dT%H:%M"),
            "id": 2,
        },
        {
            "msg": 'b',
            "star": 5,
            "created": (now + dt.timedelta(hours=1)).strftime(
                "%Y-%m-%dT%H:%M"),
            "modified": editdate,
            "id": 1,
        },
    ]})


@pytest.mark.parametrize("msgid,expect", ((1, 4), (5, None)))
def test_get_star_count_by_id(msgid, expect, example_messages, game_settings):
    with patch(
        "app.transactions.get_messages",
        return_value=({'test': example_messages}, example_messages),
    ) as get_messages:
        assert app.transactions.get_star_count_by_id(
            game_settings, 'debug', 'test', {'id': msgid},
        ) == expect
        get_messages.assert_called_with('debug', 'test', ANY)
