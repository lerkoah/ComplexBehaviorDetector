import os
import sys
from datetime import datetime
import json

class BaseDetector(object):
    def __init__(self,priority = 'DEBUG'):
        self.dectectorName = None
        self.params = None
        self.report = 'Reporting alarm'
        self.priority = priority
        self.lastError = None
        ## error log path
        self.errorLogPath = os.path.dirname(os.path.realpath(__file__)) + '/log/historical.log'

    def configure(self,params):
        self.params = params
    def execute(self):
        if self.params == 1:
            return 0
        elif self.params == 0:
            return 0

    def sendAlarm(self, timestamp, name, priority, description, detectionTime, body):
        self.lastError= '=== START ERROR: ' + priority + ' ===\n' \
                        'Timestamp: ' + timestamp + '\n' + \
                        'Detection Timestamp: '+ detectionTime + '\n' \
                        'Name: '+ name+ '\n' \
                        'Priority: '+ priority + '\n' \
                        'Description: ' + description + '\n'\
                        'Body: '+ body + '\n' \
                        '=== END ERROR ===\n'
        ## Writting in editable file
        handler = open(self.errorLogPath, 'a')
        handler.write(self.lastError)
        handler.close()

        print self.lastError
        #print self.__alarm2json(timestamp, name, priority, description, detectionTime, body)

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

    def __alarm2json(self, timestamp, name, priority, description, detectionTime, body):
        jsonFormat = '{\n' \
                     '\t"timestamp": %s,\n' \
                     '\t"Name": %s,\n' \
                     '\t"priority": %s,\n' \
                     '\t"description": %s,\n' \
                     '\t"detection_time": %s,\n' \
                     '\t"Body": %s\n' \
                     '}' %(timestamp, name, priority, description, detectionTime, body)
        return jsonFormat

# SilentTestDetector never detect
class SilentTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = 'SilentDetector'

    def execute(self):
        BaseDetector.execute(self)

# AlertingTestDetector always detect
class AlertingTestDetector(BaseDetector):
    def __init__(self, priority = 'DEBUG'):
        BaseDetector.__init__(self, priority)
        self.detectorName = 'AlertingDetector'
    def execute(self):
        BaseDetector.execute(self)
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        detectionTime = timestamp
        description = ''
        name = self.detectorName
        priority = self.priority
        body = ''

        BaseDetector.sendAlarm(self,timestamp, name, priority, description, detectionTime, body)

# HaltingTestDetector never returns
class HaltingTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = 'HaltingDetector'
    def execute(self):
        BaseDetector.execute(self)
        while True:
            pass

# RaiseErrorDetector always fails with code error, returns -1
class RaiseErrorTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = 'RaiseErrorDetector'

    def execute(priorityself):
        BaseDetector.execute(self)
        raise Exception('Error Raiser for ErrorRaiserDetector')

def main(args):
    detectorName = args[0]
    # print detectorName

    priority = None
    if len(args) > 1:
        priority = args[1]

    if detectorName == 'SilentDetector':
        myDetector = SilentTestDetector()
    elif detectorName == 'AlertingDetector':
        myDetector = AlertingTestDetector(priority)
    elif detectorName == 'HaltingDetector':
        myDetector = HaltingTestDetector()
    elif detectorName == 'RaiseErrorDetector':
        myDetector = RaiseErrorTestDetector()

    myDetector.execute()


if __name__ == '__main__':
    # print sys.argv[1:]
    main(sys.argv[1:])