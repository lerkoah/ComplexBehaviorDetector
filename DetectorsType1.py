import os
import sys
from datetime import datetime

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

    def sendAlarm(self, timestamp, uniqueID, name, priority, body):
        self.lastError= '=== START ERROR: ' + priority + ' ===\n' \
                        'timestamp: ' + timestamp + '\n' \
                        'Unique ID: '+ uniqueID + '\n' \
                        'Name: '+ name+ '\n' \
                        'Priority: '+ priority + '\n' \
                        'Body: '+ body + '\n' \
                        '=== END ERROR ===\n'
        ## Writting in editable file
        handler = open(self.errorLogPath, 'a')
        handler.write(self.lastError)
        handler.close()

        print self.lastError

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

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
        uniqueID = timestamp
        name = self.detectorName
        priority = self.priority
        body = ''

        BaseDetector.sendAlarm(self,timestamp, uniqueID, name, priority,body)

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