import os
import time
from datetime import datetime

## Function for pass YYYY-MM-DD-HH:MM:SS.MS to unix format
def fstr2unix(date):
    # Getting time object
    timeFObj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    # Converting to time.time() format
    return time.mktime(timeFObj.timetuple()) + timeFObj.microsecond / 1E6

def getIDs(errorLogPath):
    IDs = []
    t = 0
    with open(errorLogPath, 'r') as errorLog:
        for i, line in enumerate(errorLog):
            # print i
            if 2 + t * 7 == i:
                ID = fstr2unix(line[11:-1])
                if ID not in IDs:
                    IDs.append(ID)
                t += 1
    return IDs

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))

    ## Editable file
    errorLogPath = current_dir + '/historical.log'
    errorLogDBPath = current_dir + '/historicalDB.log'
    IDslist = getIDs(errorLogDBPath)
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

    ## error flag
    errorWroteFlag = 0

    ## For each error
    for t in range(numberOfErrors):
        ## Compute the unique ID in unix format
        uniqueID = fstr2unix(lines[2 + 7 * t][11:-1])

        ## If it is not the first error,
        ## then rewrite all lines beyond
        if errorWroteFlag == 1:
            for i in range(indexEnd[t] - indexStart[t] + 1):
                line = lines[indexStart[t] + i]
                errorLog.write(line)
        ## If the error has never been raised
        ## then, raise the error.
        elif not uniqueID in IDslist:
            errorWroteFlag = 1
            for i in range(indexEnd[t] - indexStart[t]+1):
                line = lines[indexStart[t]+i]
                print line[:-1]
                errorRaised.write(line)
    errorLog.close()
    errorRaised.close()

if __name__ == '__main__':
    main()