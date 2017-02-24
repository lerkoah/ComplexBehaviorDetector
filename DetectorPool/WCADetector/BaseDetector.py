import pika
import json
import argparse
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

def args():
    parser = argparse.ArgumentParser()

    parser.add_argument('-l', '--last', type=str,
                        help='Time to query ES for last logs, overrides '
                             'from/to. Example: 1s, 1m, 2h, 3d, 5w')

    parser.add_argument('-f', '--from-time', type=str,
                        help='Time lower limit in UTC')

    parser.add_argument('-t', '--to-time', type=str,
                        help='Time upper limit in UTC')

    opts = parser.parse_args()

    if opts.last is not None:
        fromTime = to_time(opts.last).isoformat()
        toTime = datetime.utcnow().isoformat()

    else:
        toTime = opts.to_time if opts.to_time is not None else 'now'
        fromTime = opts.from_time


    return {
        'from': fromTime,
        'to': toTime
    }

class BaseDetector(object):
    def __init__(self,priority = 'DEBUG'):
        self.dectectorName = None
        self.report = 'Reporting alarm'
        self.priority = priority
        self.params = None
        ## error counter
        self.errorCounter = 0

        ## RabbitMQ Parameters

        # Magic Numbers
        credentials = pika.PlainCredentials('alma', 'guest')
        host = 'ariadne.osf.alma.cl'
        port = 5672
        self.alarmQueue = 'alarm'

        # Connecting
        parameters = pika.ConnectionParameters(host, port, '/', credentials)
        connection = pika.BlockingConnection(parameters)

        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.alarmQueue)


    def configure(self,params):
        self.params = params
    def execute(self):
        if self.params == 1:
            return 0
        elif self.params == 0:
            return 0

    def sendAlarm(self, occurrence_time, name, priority, body):
        self.lastError= '=== START ERROR: ' + str(priority) + ' ===\n' \
                        '@timestamp: ' + str(occurrence_time) + '\n' + \
                        'Path: '+ str(name)+ '\n' \
                        'Priority: '+ str(priority) + '\n' \
                        'Body: '+ str(body) + '\n' \
                        '=== END ERROR ===\n'
        ## Printing in stdout
        print self.lastError

        ## Send to RabbitMQ
        jsonAlarm = json.dumps(self.__alarm2json(occurrence_time, name, priority, body))

        self.channel.basic_publish(exchange='',
                              routing_key=self.alarmQueue,
                              body=jsonAlarm,
                              properties=pika.BasicProperties(delivery_mode=2))

        self.errorCounter += 1

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

    def __alarm2json(self, occurrence_time, name, priority, body):
        jsonFormat = {
            "@timestamp": occurrence_time,
            "path": name,
            "priority": priority,
            "body": body
        }
        return jsonFormat
