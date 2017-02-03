#! /usr/bin/env python
import sys
from LogQuery import SearchAlmaELK, TimeUtils, ALMAELKHOST, QUERY_TIMEOUT
from elasticsearch_dsl.connections import connections


if __name__ == '__main__':
    fromTime = sys.argv[1]
    toTime = sys.argv[2]


    connections.create_connection(hosts=ALMAELKHOST, timeout=QUERY_TIMEOUT)

        # fromTime="2016-11-20T00:00:00.000", 
        # toTime="2016-12-08T10:00:00.000", 

        #fromTime="2016-12-07T00:00:00.000",
        #toTime="2016-12-07T23:59:59.000",
    kibana=SearchAlmaELK( index="aos64", 
        fromTime=fromTime,
        toTime=toTime,
        query='("Voltage after setting attenuation" AND /0\.2[0-1].*/) OR "Failed to move all BBs to linear zone"' ,
        limit=10000,
        reverse=False,
        columns="@timestamp,SourceObject,text",
        loglevel="DEBUG" 
    )


    tu=TimeUtils()
    known_ifprocs={}
    totalInstances = 0
    totalVoltages = 0
    totalFailed = 0

    for hit in kibana.execute().hits:
        event = hit.to_dict()
        print( kibana.format(event) )

        delete=[]

        # Timed out state
        for ifpName, oldEvent in known_ifprocs.iteritems():
            if tu.toMillis(event["@timestamp"]) - tu.toMillis(oldEvent["@timestamp"]) > 2 * 1000:
                delete.append(ifpName)

        # Start: Voltage after State
        if "Voltage after" in event["text"]:
            known_ifprocs[event["SourceObject"]] = event
            totalVoltages = totalVoltages + 1
            # print("New machine: %s" % event["SourceObject"])

        # Failed State
        elif "Failed" in event["text"]:
            totalFailed = totalFailed + 1
            if event["SourceObject"] in known_ifprocs.keys():
                # Report State
                # print("ICT-8579 Instance?")
                print("> " + kibana.format(known_ifprocs[event["SourceObject"]]) )
                print("> " + kibana.format(event) )
                print("")
                totalInstances = totalInstances + 1
                delete.append(event["SourceObject"])

        for ifpName in delete:
            # END event. Destroy machine.
            del(known_ifprocs[ifpName])
            # print("Removing machine: %s" % ifpName)

    print("ICT-8579 instances        : %s" % totalInstances)
    print("Voltages in 0.200 - 0.220 : %s" % totalVoltages)
    print("Fail to linear zone       : %s" % totalFailed)




