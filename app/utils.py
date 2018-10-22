import os


class SeralizationError(ValueError):
    pass


def serialize(game_settings, data, entry_seralizer):
    if game_settings['type'] == 'raw':
        return raw_serializer(game_settings, data, entry_seralizer)
    else:
        raise SeralizationError()


def raw_serializer(game_settings, data, entry_seralizer):
    return game_settings['line'].join(
        [
            entry_seralizer(entry, game_settings['delimiter'])
            for entry in data
        ],
    )


def scores_to_raw(entry, delim):
    return "{}{}{}{}{}".format(
        entry['rank'], delim, entry['name'], delim, entry['score'],
    )


def message_to_raw(entry, delim):
    return "{}{}{}{}{}{}{}{}{}".format(
        entry['id'], delim,
        entry['msg'], delim,
        entry['star'], delim,
        entry['created'], delim,
        entry['modified'],
    )


MAX_HIGHSCORES = int(os.environ.get("HIGHSCORE_MAX_COUNT", 100))
DEFAULT_HIGHSCORES = int(os.environ.get("DEFAULT_HIGHSCORES", 20))


def clip_highscore_count(request, game_settings):
    return min(
        int(request.args.get(
            'count',
            game_settings.get('scoresToList', DEFAULT_HIGHSCORES),
        )),
        MAX_HIGHSCORES,
    )
