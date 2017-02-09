import os
import logging
import logstash


def getIDs(raisedIDsPath):
    raisedIDs = open(raisedIDsPath, 'r')
    IDlist = raisedIDs.readlines()
    raisedIDs.close()
    return IDlist

def initializeLogger(host, port):
    logger = logging.getLogger('python-logstash-logger')
    logger.setLevel(logging.INFO)
    # test_logger.addHandler(logstash.LogstashHandler(host, 5001, version=1))
    logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))

    return logger

def sendToElastic(occurrence_time, name, priority, detectionTime, body):

    host = 'ariadne.osf.alma.cl'
    port = 5002
    logger = initializeLogger(host,port)
    print '  - Sending log to Elasticsearch.'

    print '    - Initialization in %s:%s' % (host, port)
    print '    - Creating data...',

    mylog = {
        "occurrence_time": occurrence_time,
        "Name": name,
        "priority": priority,
        "detection_time": detectionTime,
        "Body": body
    }
    print 'done.'
    print '    - Sending data...',
    logger.info(str(mylog), extra=mylog)
    print 'done.'

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))

    ## Editable file
    errorLogPath = current_dir + '/historical.log'
    errorLogDBPath = current_dir + '/historicalDB.log'
    raisedIDsPath = current_dir + '/raisedIDs.log'
    IDslist = getIDs(raisedIDsPath)
    print len(IDslist)

    ## while file is empty do nothing
    while os.stat(errorLogPath).st_size == 0:
        pass

    ## Read all lines
    errorLog = open(errorLogPath,'r')
    lines = errorLog.readlines()
    errorLog.close()

    ## Control variables
    indexStart = [i for i,line in enumerate(lines) if '=== START ERROR:' in line]
    indexEnd = [i for i,line in enumerate(lines) if '=== END ERROR ===' in line]
    numberOfErrors = len(indexStart)

    errorLog = open(errorLogPath,'w')
    errorRaised = open(errorLogDBPath,'a')
    raisedIDs = open(raisedIDsPath,'a')

    ## error flag
    errorWroteFlag = 0

    ## Control Lines
    timestampLine = 1
    nameLine = 3

    ## Alarm Parameters
    occurrence_time = ''
    detection_time = ''
    name = ''
    priority = ''
    body = ''

    ## For each error
    for t in range(numberOfErrors):
        ## Compute the unique ID in unix format
        uniqueID = lines[nameLine + indexStart[t]][6:-1] + '::'+ lines[timestampLine + indexStart[t]][11:-1]

        ## If it is not the first error,
        ## then rewrite all lines beyond
        if errorWroteFlag == 1:
            for i in range(indexEnd[t] - indexStart[t] + 1):
                line = lines[indexStart[t] + i]
                errorLog.write(line)
        ## If the error has never been raised
        ## then, raise the error.
        elif not (uniqueID+'\n') in IDslist and errorWroteFlag == 0:
            errorWroteFlag = 1
            for i in range(indexEnd[t] - indexStart[t]+1):
                line = lines[indexStart[t]+i]
                print line[:-1]
                errorRaised.write(line)

                if 'Occurrence Time' in line:
                    occurrence_time = line[17:]
                elif 'Detection Timestamp' in line:
                    detection_time = line[21:]
                elif 'Name' in line:
                    name = line[6:]
                elif 'Priority' in line:
                    priority = line[10:]
                elif 'Body' in line:
                    body = line[6:]
            ## Send to Elasticsearch the alarm
            sendToElastic(occurrence_time,name,priority,detection_time, body)
            raisedIDs.write(uniqueID + '\n')


    errorLog.close()
    errorRaised.close()
    raisedIDs.close()

if __name__ == '__main__':
    main()