#! /usr/bin/env python
import sys
from elasticsearch_dsl.connections import connections
from LogQuery import *
from ProcessModel import *


class WCALockFail(ProcessModel):

    # Each declared symbol will be added in trace. Even if it is not part of any transition.
    # Trick!!! e['name'] in e['Process']  is to filter out events from other antennas
    symbols={
        'tuning': lambda e: 'Tuning Values'  in e['text'] and e['name'] in e['Process'],
        'lock':   lambda e: 'WCA Locked'     in e['text'] and e['name'] in e['Process'],
        'fail':   lambda e: 'Lock FAILED'    in e['text'] and e['name'] in e['Process'],
        'retry':  lambda e: 'Re-trying lock' in e['text'] and e['name'] in e['Process']
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
        e["name"] = self.id
        return e



if __name__ == '__main__':


    fromTime = sys.argv[1]
    toTime = sys.argv[2]

    # Know timeframe where this issue happens
    #fromTime = "2017-02-01T05:00:50.463"
    #toTime = "2017-02-01T05:20:22.184"


    # a single line should be enough, but splitted is more clear
    query = []
    query.append('Tuning Values')
    query.append('Lock FAILED')
    query.append('WCA Locked')
    query.append('Re-trying lock')

    queryString = "FrontEnd AND (" + " OR ".join([ " \"%s\" " % q for q in query]) + ")"

    print ("Searching on Kibana with query: %s\n" % queryString)

    connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

    kibana=SearchAlmaELK( index="online",
        fromTime=fromTime,
        toTime=toTime,
        query=queryString,
        limit=10000,
        columns="@timestamp,origin,SourceObject,text",
    )



    # The magic is here!
    log = LogIterator( model=WCALockFail, verbose=False, reportingStates=['FOUND'], formatLog=kibana.format  )
    log.process( dataset=kibana.execute().hits )

    print( log.summary() )