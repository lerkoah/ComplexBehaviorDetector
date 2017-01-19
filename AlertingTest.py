from DetectorsType1 import *
def main():
    # myDetector = SilentTestDetector()
    myDetector = AlertingTestDetector()
    # myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    myDetector.execute()

if __name__ == '__main__':
    main()