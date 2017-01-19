from DetectorsType1 import *

def main():
    myDetector = SilentTestDetector()
    # myDetector = AlertingTestDetector()
    # myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    detection = myDetector.execute()

    if detection == 1:
        myDetector.sendAlarm()
    elif detection == -1:
        raise SystemError('Error code 123')



if __name__ == '__main__':
    main()