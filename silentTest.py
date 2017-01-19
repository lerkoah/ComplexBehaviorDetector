from DetectorsType1 import *

def main():
    myDetector = SilentTestDetector()
    # myDetector = AlertingTestDetector()
    # myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    try:
        myDetector.execute()
    except:
        return -1


if __name__ == '__main__':
    main()