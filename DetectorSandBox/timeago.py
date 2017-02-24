from datetime import datetime, timedelta


SECONDS_PER_UNIT = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}


def to_time(s, now=None):
    """
    Receives a delta of time string, and calculates a past time with that
    delta. The string is formatted as <INT><UNIT>, where UNIT is one of s
    (seconds), m (minutes), h (hours), d (days), w (weeks).

    For example:

    Using 1 day as delta.
    >>> to_time('1d', now=datetime(2017, 02, 16, 2))
    datetime.datetime(2017, 2, 15, 2, 0)

    Using 1 week as delta.
    >>> to_time('1w', now=datetime(2017, 02, 16, 2))
    datetime.datetime(2017, 2, 9, 2, 0)

    It should fail when the format is not recognized.
    >>> to_time('1t')
    Traceback (most recent call last):
    ...
    SyntaxError: not a valid time unit: t, must be one of s, m, h, d, w

    :param s: the delta of time as an string
    :param now: optional now argument for easy testing
    :return: a resulting datetime object
    """
    try:
        number = int(s[:-1])
    except ValueError:
        raise SyntaxError('not an integer number: %s' % s[:-1])

    unit = s[-1]
    if unit not in SECONDS_PER_UNIT:
        raise SyntaxError('not a valid time unit: %s, '
                          'must be one of s, m, h, d, w' % unit)

    if now is None:
        now = datetime.utcnow()
    else:
        if not isinstance(now, datetime):
            raise ValueError('`now` argument must be a datetime')

    return now - timedelta(seconds=number * SECONDS_PER_UNIT[unit])