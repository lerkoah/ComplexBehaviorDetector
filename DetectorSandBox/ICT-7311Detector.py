#! /usr/bin/env python
import sys
from elasticsearch_dsl.connections import connections
from LogQuery import *
from ProcessModel import *
import time
from BaseDetector import *

class BDFrameAckStartSend(ProcessModel):

    # Each declared symbol will be added in trace. Even if it is not part of any transition.
    # Trick!!! e['name'] in e['Process']  is to filter out events from other antennas
    symbols={
        'BD-timeout':  lambda e: 'BD Frame Ack Timeout'              in e['text'],
        'startSend' :  lambda e: 'startSend error'                   in e['text'],
        'generalErr':  lambda e: 'General bulkdata error'            in e['text'],
        'err-caught':  lambda e: 'bulk data error caught!'           in e['text'],
        'failed-flow': lambda e: 'failed to start flow transference' in e['text'],
        '(event too old to live)': lambda e:   e['seconds'] > 1.0
    }

    # Try to keep this as simple as possible
    states = {
        'INIT': {
            'transitions' : { '(event too old to live)': 'END_SILENTLY' },
            # All these symbols must be present to go to the next State
            'AND' : {
                'symbols': ['BD-timeout', 'startSend'],
                'nextState' : 'TIMED_OUT'
            },
            'isStartState': True
        },
        'TIMED_OUT': {
            'transitions' : {
                '(event too old to live)': 'END_SILENTLY',
                'failed-flow': 'FOUND'
            },
            # All these symbols must be present to go to the next State
            'AND' : {
                'symbols': ['generalErr', 'err-caught'],
                'nextState' : 'FOUND'
            }
        },
        'END_SILENTLY':   {},
        'FOUND': {}
    }


    # When should I start a new process?
    @staticmethod
    def creationEvent(e):
        try:
            return 'BD Frame Ack Timeout' in e['text'] or 'startSend error' in e['text']
        except:
            return False

    # Name for new process, CM11 in CONTROL/CM11/...
    def idBasedOnEvent(self, e):
        return "Instance at %s" % e["@timestamp"]

    # Add more fields to events
    def preprocessEvent(self, e):
        e["seconds"] = self.addElapsedSeconds(e)
        return e

class ICT7311Detector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = 'BDFrameACKStartSend'
        self.priority = 'WARNING'
        self.prefix = 'ONLINE/Issues/MULTILINER/'.upper()

    def configure(self,fromTime,toTime):
        self.fromTime = fromTime
        self.toTime = toTime

    def execute(self):
        # fromTime = sys.argv[1]
        # toTime = sys.argv[2]

        # Know timeframe where this issue happens
        # fromTime = "2017-02-01T05:00:50.463"
        # toTime = "2017-02-01T05:20:22.184"


        # a single line should be enough, but splitted is more clear
        query = []
        query.append('startSend error')
        query.append('BD Frame Ack Timeout')
        query.append('General bulkdata error')
        query.append('bulk data error caught')
        query.append('Wrong sender command order')
        query.append('failed to start flow transference')

        queryString = "(" + " OR ".join([" \"%s\" " % q for q in query]) + ")"

        print ("Searching on Kibana with query: %s\n" % queryString)

        connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        kibana = SearchAlmaELK(index="online",
                               fromTime=self.fromTime,
                               toTime=self.toTime,
                               query=queryString,
                               limit=10000,
                               columns="@timestamp,origin,SourceObject,text",
                               )

        def sendAlarmHandler(modelInstance):

            eventSequence = modelInstance.getTrace()
            firstEvent = eventSequence[0]
            path = self.prefix + self.detectorName
            path = path.upper()

            self.sendAlarm(firstEvent['@timestamp'], path, self.priority, eventSequence)

        # The magic is here!
        log = LogIterator(model=BDFrameAckStartSend, verbose=False, verboseTransitions=False, reportingStates=['FOUND'],
                          formatLog=kibana.format, reportingCallback=sendAlarmHandler)
        log.process(dataset=kibana.execute().hits)

        print(log.summary())

    def executeTruePositive(self):
        # self.configure('2016-12-12T23:15:45.170','2016-12-12T23:16:41.453')
        self.configure('2017-01-25T00:00:00.000','2017-01-25T23:59:59.540')
        self.execute()

    def executeFalseNegative(self):
        self.configure('2017-02-13T03:47:40.565','2017-02-13T15:47:40.566')
        self.execute()

if __name__ == '__main__':
    options = args()

    myDetector = ICT7311Detector()
    myDetector.configure(options['from'], options['to'])

    tic = time.time()
    if options['tp']:
        myDetector.executeTruePositive()
    elif options['fn']:
        myDetector.executeFalseNegative()
    else:
        myDetector.execute()
    toc = time.time() - tic
    print 'Elapse [seg]: %s' % toc