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
