from BaseDetector import BaseDetector
from LogQuery import SearchAlmaELK, TimeUtils, ALMAELKHOST, QUERY_TIMEOUT
from elasticsearch_dsl.connections import connections
import json
from FSMlog import FSMLog, processEvents


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class WCA(FSMLog):
    triggerCreationSymbol = "Tuning"  # Triggering FSM creation
    startState = "StateTuning"
    symbols = {
        "Tuning": lambda e: "Tuning Values"  in e["text"],
        "Locked": lambda e: "WCA Locked"     in e["text"],
        "Fail"  : lambda e: "Lock FAILED"    in e["text"],
        "Retry" : lambda e: "Re-trying lock" in e["text"]
    }
    transitions = {
        "StateTuning": [
            {"symbol": "Fail", "nextState": "StateFail"},  # Receive Fail 1 then go to StateFail
            {"symbol": "Locked", "nextState": "END"}  # Receive Locked then go to END

        ],
        "StateFail": [
            {"symbol": "Retry", "nextState": "StateRetry"}  # Receive Retry then go to StateRetry
        ],
        "StateRetry": [
            {"symbol": "Tuning", "nextState": "StateReTuning"}  # Receive Fail 2 then go to StateReTuning
        ],
        "StateReTuning": [
            {"symbol": "Fail", "nextState": "FOUND"},  # Receive Fail 2 then go to StateFail_2
            {"symbol": "Locked", "nextState": "END"}  # Receive Locked then go to END
        ],
    }

    def getNameFromEvent(self, event):
        name = ''
        if 'Tuning Values' in event['text']:
            name = 'Tuning'
        elif 'WCA Locked' in event['text']:
            name = 'Locked'
        elif 'Lock FAILED' in event['text']:
            name = 'Fail'
        elif 'Re-trying lock' in event['text']:
            name = 'Retry'
        return name


class WCADetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = 'WCA'
        self.priority = 'WARNING'
        self.prefix = 'ONLINE/Issues/OneLiner/'.upper()

    def configure(self,fromTime,toTime):
        self.fromTime = fromTime
        self.toTime = toTime
    def execute(self):
        BaseDetector.execute(self)
        detectorQuery = '("Tuning Values" OR "Lock FAILED" OR "WCA Locked" OR "Re-trying lock")'
        connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        myname = self.detectorName.upper()
        kibana = SearchAlmaELK(index="online",
                               fromTime=self.fromTime,
                               toTime=self.toTime,
                               query=detectorQuery,
                               limit=10000,
                               columns="@timestamp,SourceObject,text",
                               loglevel="DELOUSE"
                               )
        kibanaHits = kibana.execute().hits
        print '- Searching for : ' + myname + '; query: ' + detectorQuery
        print '  - Number of queries found: ' + str(len(kibanaHits))

        print '\n- Processing results'
        logSummary = {}
        for j in range(len(kibanaHits)):
            hit = kibanaHits[j]
            event = hit.to_dict()
            antenna = event['SourceObject'].split('/')[1]
            try:
                logSummary[antenna].append({'@timestamp': event['@timestamp'], 'text': event['text']})
            except KeyError:
                logSummary[antenna] = [{'@timestamp': event['@timestamp'], 'text': event['text']}]

        for antenna in logSummary.keys():
            # lockCounter = 0
            # print '  - Antenna:  '+antenna
            # for event in logSummary[antenna]:
            #     if 'Lock FAILED' in event['text'] and lockCounter == 0:
            #         print bcolors.WARNING + '    - '+event['@timestamp']+' : '+event['text'] + bcolors.ENDC
            #         lockCounter += 1
            #     elif 'Lock FAILED' in event['text'] and lockCounter == 1:
            #         print bcolors.FAIL + '    - '+event['@timestamp']+' : '+event['text'] + bcolors.ENDC
            #     else:
            #         print '    - '+event['@timestamp']+' : '+event['text']
            print bcolors.HEADER + '## Antenna '+antenna + ' ##'+ bcolors.ENDC
            occurrence_time = processEvents(WCA, logSummary[antenna]) or False

            if occurrence_time is not False:
                self.sendAlarm(occurrence_time, self.detectorName, self.priority, {antenna: logSummary[antenna]})
                # print bcolors.FAIL + '###### WCA FAILED at %s######' % valueLogs + bcolors.
        # print json.dumps(logSummary, indent=1)


    def executeTruePositive(self):
        self.configure('2017-02-01T05:08:18.341','2017-02-01T05:15:18.341')
        self.execute()

if __name__ == '__main__':
    myDetector = WCADetector()
    myDetector.executeTruePositive()