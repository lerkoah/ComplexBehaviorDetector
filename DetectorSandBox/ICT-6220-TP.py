#! /usr/bin/env python
import sys
from LogQuery import SearchAlmaELK, TimeUtils, ALMAELKHOST, QUERY_TIMEOUT
from elasticsearch_dsl.connections import connections



class ICT6220Fsm:
    # Symbols Lambda Dictionary
    symbols={
        "StreamCreated":      lambda e: e["streamName"] in e["text"] and "Sender Stream" in e["text"] and "created" in e["text"],
        "StreamDestroyed":    lambda e: e["streamName"] in e["text"] and "Sender Stream" in e["text"] and "destroyed" in e["text"],
        "FlowCreated":        lambda e: e["streamName"] in e["text"] and "Sender Flow" in e["text"]   and "created" in e["text"],
        "FlowDestroyed":      lambda e: e["streamName"] in e["text"] and "Sender Flow" in e["text"]   and "destroyed" in e["text"],
        "Error in TP":        lambda e: "TOTALPOWER" in e["Process"] and ("Error" in e["LogLevel"] or "Warning" in e["LogLevel"]),
        "Time out archiving": lambda e: "Timed out" in e["text"] and "total-power processor to archive" in e["text"] and "SSR" not in e["SourceObject"],
        "Observing done":     lambda e: "observing mode shutting down" in e["text"],
        "Aborting digitizers":     lambda e: "Aborting subscan" in e["text"] and "digitizers" in e["text"],
        "Aborting DataCollectors": lambda e: "Aborting subscan" in e["text"] and "DataCollectors" in e["text"]
        # "Aborting digitizers":     lambda e: e["arrayName"] in e["SourceObject"] and "Aborting subscan" in e["text"] and "digitizers" in e["text"],
        # "Aborting DataCollectors": lambda e: e["arrayName"] in e["SourceObject"] and "Aborting subscan" in e["text"] and "DataCollectors" in e["text"]
    }

    # This is the expected NORMAL flow.
    transitions = {
        "INIT": [ 
            {"symbol": "StreamCreated", "nextState": "STREAM_C"} 
        ],
        "STREAM_C" : [
            {"symbol": "FlowCreated", "nextState": "FLOW_C"}, 
        ],
        "FLOW_C" : [
            {"symbol": "FlowDestroyed", "nextState": "FLOW_D"},
            {"symbol": "StreamDestroyed", "nextState": "STREAM_D"},
            {"symbol": "Error in TP", "nextState": "FLOW_C"},
            {"symbol": "Aborting digitizers", "nextState": "FLOW_C"},
            {"symbol": "Aborting DataCollectors", "nextState": "FLOW_C"},
            {"symbol": "Time out archiving", "nextState": "FLOW_C"}
            # {"symbol": "Observing done", "nextState": "END"}
        ],
        "SHUTDOWN" : [
        ],
        "ABORTED_DIG": [
            # {"symbol": "Error in TP", "nextState": "ABORTED_DIG"},
            # {"symbol": "Aborting DataCollectors", "nextState": "ABORTED_COLL"}
        ],
        "ABORTED_COLL": [
            # {"symbol": "Error in TP", "nextState": "ABORTED_COLL"},
            # {"symbol": "FlowDestroyed", "nextState": "FLOW_D"},
            # {"symbol": "StreamDestroyed", "nextState": "STREAM_D"}
        ],
        "FLOW_D" : [
            {"symbol": "StreamDestroyed", "nextState": "END"}
        ],
        "STREAM_D" : [
            {"symbol": "FlowDestroyed", "nextState": "END"}
        ],
        "TIMED_OUT": [
            {"symbol": "Error in TP", "nextState": "TIMED_OUT"},
            {"symbol": "Aborting digitizers", "nextState": "TIMED_OUT"},
            {"symbol": "Aborting DataCollectors", "nextState": "TIMED_OUT"},
            {"symbol": "Time out archiving", "nextState": "TIMED_OUT"},
            {"symbol": "FlowDestroyed", "nextState": "FLOW_D"},
            {"symbol": "StreamDestroyed", "nextState": "STREAM_D"},
        ],
        "ERROR" : [],
        "END" : []

    }


    def __init__(self):
        self.state = "INIT"
        self.events = []
        self.streamName = "LLENAR"
        self.arrayName = "LLENAR"

    def parseSymbol(self,event):
        # ESTO ES FEO pero sirve :P
        if "Array" in event["SourceObject"] and "Timed out" in event["text"] and self.arrayName == "LLENAR":
            self.arrayName = event["SourceObject"].split("/")[1]

        # Prefill some values
        event["streamName"] = self.streamName
        event["arrayName"] = self.arrayName

        # check if event is in my grammar
        ALLOWED = False
        for symbol, func in self.symbols.iteritems():
            ALLOWED = ALLOWED or func(event) 
        if not ALLOWED:
            # print ("WARNING!! Not allowed symbol: %s " % event)
            return

        found = False
        for t in self.transitions[ self.state ]:
            if self.symbols[t["symbol"]]( event ):
                if found:
                    raise ValueError("Duplicated symbol! This is should be a deterministic machine.")
                else:
                    self.setState(t["nextState"], event)
                    # print ("%s : symbol found = %s " % (self.streamName, t["symbol"]))
                    found = True
        if not found:
            # any non recognized symbol MUST be an 
            nextAllowSymbols = [t["symbol"] for t in self.transitions[ self.state ]]
            print ("%s : from state %s, next allowed event (%s) NOT FOUND " % (self.streamName, self.state, nextAllowSymbols ))
            self.setState( "ERROR", event )

    def setState(self, next, event):
        self.events.append(event)
        self.state = next


if __name__ == '__main__':

    fromTime = sys.argv[1]
    toTime = sys.argv[2]


    query = []
    query.append('TOTALPOWER AND ("Sender Stream:" "Sender Flow:") AND "has been"')
    query.append('"CONTROL/ACC/javaContainer" AND "total-power processor to archive"')
    query.append('"client timeout reached"')
    query.append('TOTALPOWER AND (Error OR Warning) AND -("NDDS_DISCOVERY_PEERS" "Assuming connection" "while receiving packets" "ignoring subscan" "not (yet) connected")')
    query.append('"Aborting subscan on all digitizers"')
    query.append('"Aborting subscans on all DataCollectors"')


    queryString = " OR ".join([ "(%s)" % q for q in query])

    print "Searching on Kibana with query:"
    print
    print queryString
    print

    connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

    kibana=SearchAlmaELK( index="ape1", 
        fromTime=fromTime, # fromTime="2016-12-06T22:49:50.601",
        toTime=toTime,
        query=queryString,
        limit=10000,
        reverse=False,
        columns="TimeStamp,SourceObject,text,Data.text",
        loglevel="DEBUG" 
    )



    tu=TimeUtils()
    machines={}

    for hit in kibana.execute().hits:
        event = hit.to_dict() 
        # print (event)
        # print( kibana.format(event) )

        if "Sender Stream" in event["text"] and "created" in event["text"]:
            # Create new machine
            streamName = event["text"].split()[2] # TotalPowerStream5
            if streamName not in machines.keys():
                machines[streamName] = ICT6220Fsm()
                machines[streamName].streamName = streamName

        destroy = []
        for name, mach in machines.iteritems():
                mach.parseSymbol(event)
                # print ("%s : %s" % (name, mach.state))

                if mach.state == "END":
                    destroy.append(name)
                elif mach.state == "ERROR":
                    print 
                    print ("-------- %s instance found --------" % mach.__class__.__name__)
                    for event in mach.events:
                        print( kibana.format(event) )
                    print 
                    destroy.append(name)

        for name in destroy:
            del( machines[name] )
            # print ("%s : Destroyed !" % name)






