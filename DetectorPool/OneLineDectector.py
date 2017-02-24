from BaseDetector import *
from LogQuery import SearchAlmaELK, TimeUtils, ALMAELKHOST, QUERY_TIMEOUT
from elasticsearch_dsl.connections import connections
from one_line_db import one_line_db
import getKibanaQueries
import time
from datetime import datetime, timedelta


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class OneLineDetector(BaseDetector):
    def __init__(self, priority = 'INFO'):
        BaseDetector.__init__(self)
        self.detectorName = None

        # Priority IDs: CRITICAL = 0; WARNING = 1,2; INFO = 3
        self.priority = ['CRITICAL', 'WARNING', 'WARNING', 'INFO']

        self.prefix = 'ONLINE/Issues/OneLiner/'.upper()

    def configure(self,fromTime,toTime):
        self.fromTime = fromTime
        self.toTime = toTime
    def execute(self):
        BaseDetector.execute(self)

        connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        counter = 0
        for myname, myquery, priorityID in getKibanaQueries.getQueries():
        # for myname, myquery, priorityID in one_line_db().getQueries():
            myname = myname.upper()
            kibana = SearchAlmaELK(index="online",
                                   fromTime=self.fromTime,
                                   toTime=self.toTime,
                                   query=myquery,
                                   limit=1,
                                   columns="@timestamp,SourceObject,text",
                                   loglevel="DELOUSE"
                                   )
            # previousEvent = {"@timestamp": "1969-12-31T21:00:00"}

            kibanaHits = kibana.execute().hits
            print '- Searching for : ' + myname + '; query: ' + myquery
            print '  - Number of queries found: ' +str(len(kibanaHits))

            for j in range(len(kibanaHits)):
                hit = kibanaHits[j]
                event = hit.to_dict()
                fullDetectionTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
                detectionTime = fullDetectionTime[0:23] + 'Z'

                priority = self.priority[priorityID]

                self.sendAlarm(event["@timestamp"], self.prefix + myname, priority, event)
                counter += 1

                # print(bcolors.FAIL + "     - " + kibana.format(event) + bcolors.ENDC)
                # previousEvent["@timestamp"] = event["@timestamp"]
        print 'Total Errors: %i' % counter

def main():
    options = args()
    myDetector = OneLineDetector()
    ## Some True Positive examples
    # myDetector.configure("2017-02-01T00:00:00.000", "2017-02-01T23:59:59.000")
    # myDetector.configure("2017-01-21T00:00:00.000", "2017-01-21T03:00:00.000")

    myDetector.configure(options['from'], options['to'])
    tic = time.time()
    myDetector.execute()

    toc = time.time() - tic
    print 'Elapse [seg]: %s' % toc


if __name__ == '__main__':
    main()