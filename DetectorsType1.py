import threading
import time
import socket

def clientSocket(alarmType, detectorName, alarmReport):
    HOST = ''  # Symbolic name meaning all available interfaces
    PORT = 8889  # Arbitrary non-privileged port

    s = socket.socket()
    s.connect((HOST, PORT))
    msg = alarmType + ':::' + detectorName+ ':::' + alarmReport
    s.send(msg)

    s.close()

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
        clientSocket(self.alarmType, self.dectector ,self.report)
        # print 'ERROR '+ time.asctime( time.localtime(time.time()) )
        # time.sleep(10)
        # print 'ERROR2 ' + time.asctime(time.localtime(time.time()))

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
        return -1

def main():
    # myDetector = SilentTestDetector()
    myDetector = AlertingTestDetector()
    # myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    myDetector.execute()






if __name__ == '__main__':
    main()