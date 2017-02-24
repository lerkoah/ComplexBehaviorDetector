from BaseDetector import *
from LogQuery import *
from ProcessModel import *
import time


class WCALockFail(ProcessModel):

    # Each declared symbol will be added in trace. Even if it is not part of any transition.
    # Trick!!! e['name'] in e['Process']  is to filter out events from other antennas
    symbols={
        'tuning': lambda e: 'Tuning Values'  in e['text'] and e['antenna_name'] in e['Process'],
        'lock':   lambda e: 'WCA Locked'     in e['text'] and e['antenna_name'] in e['Process'],
        'fail':   lambda e: 'Lock FAILED'    in e['text'] and e['antenna_name'] in e['Process'],
        'retry':  lambda e: 'Re-trying lock' in e['text'] and e['antenna_name'] in e['Process']
    }

    # Try to keep this as simple as possible
    states = {
        'INIT': {
            'transitions' : { 'tuning': 'START_TUNING' }, 'isStartState': True
        },
        'START_TUNING': {
            'transitions' : { 'lock': 'END', 'retry': 'FAIL_1' }
        },
        'FAIL_1': {
            'transitions' : { 'tuning': 'TUNE_2' }
        },
        'TUNE_2': {
            'transitions' : { 'lock': 'END', 'fail': 'FOUND' }
        },
        'END':   {},
        'FOUND': {}
    }


    # When should I start a new process?
    @staticmethod
    def creationEvent(e):
        try:
            return 'Tuning Values' in e['text']
        except:
            return False

    # Name for new process, CM11 in CONTROL/CM11/...
    def idBasedOnEvent(self, e):
        return e["Process"].split("/")[1]

    # Add more fields to events
    def preprocessEvent(self, e):
        e["antenna_name"] = self.id
        return e


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class WCADetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = 'WCA'
        self.priority = 'WARNING'
        self.prefix = 'ONLINE/Issues/MULTILINER/'.upper()

    def configure(self,fromTime,toTime):
        self.fromTime = fromTime
        self.toTime = toTime
    def execute(self):
        BaseDetector.execute(self)
        fromTime = self.fromTime
        toTime = self.toTime

        # Know timeframe where this issue happens
        # fromTime = "2017-02-01T05:00:50.463"
        # toTime = "2017-02-01T05:20:22.184"


        # a single line should be enough, but splitted is more clear
        query = []
        query.append('Tuning Values')
        query.append('Lock FAILED')
        query.append('WCA Locked')
        query.append('Re-trying lock')

        queryString = "FrontEnd AND (" + " OR ".join([" \"%s\" " % q for q in query]) + ")"

        print ("Searching on Kibana with query: %s\n" % queryString)

        connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        kibana = SearchAlmaELK(index="online",
                               fromTime=fromTime,
                               toTime=toTime,
                               query=queryString,
                               limit=10000,
                               columns="@timestamp,origin,SourceObject,text",
                               )


        def sendAlarmHandler(modelInstance):

            eventSequence = modelInstance.getTrace()
            firstEvent = eventSequence[0]
            antenna = modelInstance.id
            path = self.prefix + 'WCA/' + antenna

            self.sendAlarm(firstEvent['@timestamp'], path, self.priority, {antenna: eventSequence})

        # The magic is here!
        log = LogIterator(model=WCALockFail, verbose=False, reportingStates=['FOUND'], formatLog=kibana.format, reportingCallback=sendAlarmHandler)
        log.process(dataset=kibana.execute().hits)

        print 'Total number of errors: %i' % self.errorCounter

    def executeTruePositive(self):
        self.configure('2017-01-11T00:00:00.000','2017-01-12T00:00:00.000')
        self.execute()

if __name__ == '__main__':
    options = args()

    myDetector = WCADetector()
    # myDetector.executeTruePositive()
    myDetector.configure(options['from'], options['to'])

    tic = time.time()
    myDetector.execute()
    toc = time.time() - tic
    print 'Elapse [seg]: %s' % toc
