class BaseDetector(object):
    def __init__(self):
        self.dectector = 0
        self.params = None
        self.report = 'Reporting alarm'
    def configure(self,params):
        self.params = params
    def execute(self):
        if self.params == 1:
            return 0
        elif self.params == 0:
            return 0

    def sendAlarm(self):
        # print self.report
        raise Exception(self.report)
    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

# SilentTestDetector never detect
class SilentTestDetector(BaseDetector):
    def execute(self):
        BaseDetector.execute(self)
        return 0

# AlertingTestDetector always detect
class AlertingTestDetector(BaseDetector):
    def execute(self):
        BaseDetector.execute(self)
        return 1
# HaltingTestDetector never returns
class HaltingTestDetector(BaseDetector):
    def execute(self):
        BaseDetector.execute(self)
        while True:
            pass

# RaiseErrorDetector always fails with code error, returns -1
class RaiseErrorTestDetector(BaseDetector):
    def execute(self):
        BaseDetector.execute(self)
        return -1
def main():
    # myDetector = SilentTestDetector()
    # myDetector = AlertingTestDetector()
    myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    detection = myDetector.execute()

    if detection == 1:
        myDetector.sendAlarm()
    elif detection == -1:
        raise SystemError('Error code 123')



if __name__ == '__main__':
    main()