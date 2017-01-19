import threading
import time

class BaseDetector(object):
    def __init__(self):
        self.dectector = None
        self.params = None
        self.report = 'Reporting alarm'
        self.alarmType = 'Normal'
    def configure(self,params):
        self.params = params
    def execute(self):
        if self.params == 1:
            return 0
        elif self.params == 0:
            return 0

    def sendAlarm(self):
        print 'ERROR '+ time.asctime( time.localtime(time.time()) )

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

# SilentTestDetector never detect
class SilentTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.dectector = 'SilentDetector'

    def execute(self):
        BaseDetector.execute(self)

# AlertingTestDetector always detect
class AlertingTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.dectector = 'AlertingDetector'
    def execute(self):
        BaseDetector.execute(self)
        BaseDetector.sendAlarm(self)

# HaltingTestDetector never returns
class HaltingTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.dectector = 'HaltingDetector'
    def execute(self):
        BaseDetector.execute(self)
        while True:
            pass

# RaiseErrorDetector always fails with code error, returns -1
class RaiseErrorTestDetector(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.dectector = 'RaiseErrorDetector'
    def execute(self):
        BaseDetector.execute(self)
        raise Exception('Error Raiser for ErrorRaiserDetector')

def main():
    # myDetector = SilentTestDetector()
    myDetector = AlertingTestDetector()
    # myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    myDetector.execute()


if __name__ == '__main__':
    main()