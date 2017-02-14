from BaseDetector import BaseDetector
from LogQuery import SearchAlmaELK, TimeUtils, ALMAELKHOST, QUERY_TIMEOUT
from elasticsearch_dsl.connections import connections
from datetime import datetime
from one_line_db import one_line_db
import getKibanaQueries
import time

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class ICTListDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = None
        self.priority = 'INFO'
        self.prefix = 'ONLINE/Issues/OneLiner/'

    def configure(self,fromTime,toTime):
        self.fromTime = fromTime
        self.toTime = toTime
    def execute(self):
        BaseDetector.execute(self)

        connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        # for myname, myquery in getKibanaQueries.getQueries():
        kibanaHitsList = []
        oneLineDB = one_line_db().getQueries()
        for myname, myquery in oneLineDB:
            kibana = SearchAlmaELK(index="online",
                                   fromTime=self.fromTime,
                                   toTime=self.toTime,
                                   query=myquery,
                                   limit=1,
                                   columns="@timestamp,SourceObject,text",
                                   loglevel="DELOUSE"
                                   )
            kibanaHitsList.append(kibana.execute().hits)

        for it in range(1667):
            counter = 0
            for ii in range(len(kibanaHitsList)):
                kibanaHits = kibanaHitsList[ii]
                myname = oneLineDB[ii][0]
                myquery = oneLineDB[ii][1]
                print '- Searching for : ' + myname + '; query: ' + myquery
                print '  - Number of queries found: ' +str(len(kibanaHits))

                for j in range(len(kibanaHits)):
                    hit = kibanaHits[j]
                    event = hit.to_dict()
                    fullDetectionTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
                    detectionTime = fullDetectionTime[0:23] + 'Z'

                    self.sendAlarm(event["@timestamp"], self.prefix + myname, self.priority, detectionTime, event)
                    counter += 1

                    # print(bcolors.FAIL + "     - " + kibana.format(event) + bcolors.ENDC)
                    # previousEvent["@timestamp"] = event["@timestamp"]
                print 'Total Errors: %i' % counter

def main():
    myDetector = ICTListDetector()
    myDetector.configure("2017-02-01T00:00:00.000", "2017-02-01T23:59:59.000")
    # myDetector.configure("2017-01-21T00:00:00.000", "2017-01-21T03:00:00.000")
    tic = time.time()
    myDetector.execute()

    toc = time.time() - tic
    print 'Elapse [seg]: %s' % toc


if __name__ == '__main__':
    main()