from BaseDetector import *
from LogQuery import *
from ProcessModel import *
import time


class ICT9048FSM(ProcessModel):

    # Each declared symbol will be added in trace. Even if it is not part of any transition.
    symbols={
        'sub-array': lambda e: 'antennas in sub-array' in e['text'],
        'started':   lambda e: 'bdf started' in e['text'],
        'splitting': lambda e: 'while splitting off imhs ran into invalid start time' in e['text']
    }

    # Try to keep this as simple as possible
    states = {
        'INIT': {
            'transitions' : { 'sub-array': 'SUB-ARRAY' }, 'isStartState': True
        },
        'SUB-ARRAY': {
            'transitions' : { 'started': 'BDF' }
        },
        'BDF': {
            'transitions' : { 'splitting': 'FOUND', 'sub-array': 'END' }
        },
        'END':   {},
        'FOUND': {}
    }


    # When should I start a new process?
    @staticmethod
    def creationEvent(e):
        try:
            return 'antennas in sub-array' in e['text']
        except:
            return False

    # Name for new process
    def idBasedOnEvent(self, e):
        return e["Process"].split("/")[1]

    # Add more fields to events
    def preprocessEvent(self, e):
        e["name"] = self.id
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

class ICT9048Detector(BaseDetector):
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

        # a single line should be enough, but splitted is more clear
        query = []
        query.append('antennas in sub-array')
        query.append('bdf started')
        query.append('while splitting off imhs ran into invalid start time')

        queryString = "("+" OR ".join([" \"%s\" " % q for q in query]) + ")"

        print ("Searching on Kibana with query: %s\n" % queryString)

        connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        kibana = SearchAlmaELK(index="online",
                               fromTime=fromTime,
                               toTime=toTime,
                               query=queryString,
                               limit=10000,
                               columns="@timestamp,origin,SourceObject,text",
                               )
        kibanaHits = kibana.execute().hits
        sequence = []
        for j in range(2,len(kibanaHits)):
            hit = kibanaHits[j]
            event = hit.to_dict()
            if 'while splitting off imhs ran into invalid start time' in event["text"]:
                if kibanaHits[j - 2] not in sequence:
                    sequence.append(kibanaHits[j - 2])
                if kibanaHits[j - 1] not in sequence:
                    sequence.append(kibanaHits[j - 1])
                sequence.append(kibanaHits[j])

        def sendAlarmHandler(modelInstance):

            eventSequence = modelInstance.getTrace()
            firstEvent = eventSequence[0]
            path = self.prefix + 'ICT-9048'

            self.sendAlarm(firstEvent['@timestamp'], path, self.priority, eventSequence)

        # The magic is here!
        log = LogIterator(model=ICT9048FSM, verbose=False, reportingStates=['FOUND'], formatLog=kibana.format, reportingCallback=sendAlarmHandler)
        log.process(dataset=sequence)



    def executeTruePositive(self):
        # self.configure('2017-01-07T20:13:35.322','2017-01-07T20:14:37.967')
        self.configure('2017-01-07T20:12:35.322','2017-01-07T20:15:37.967')
        self.execute()

    def executeFalseNegative(self):
        self.configure('2017-02-13T03:47:40.565','2017-02-13T15:47:40.566')
        self.execute()

if __name__ == '__main__':
    options = args()

    myDetector = ICT9048Detector()
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