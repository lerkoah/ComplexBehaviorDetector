from BaseDetector import BaseDetector
import string
import random
from datetime import datetime
import sys

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

class RandomAlarmGenerator(BaseDetector):
    def __init__(self):
        BaseDetector.__init__(self)
        self.detectorName = id_generator()
        priorityList = ['INFO',
                        'WARNING',
                        'CRITICAL']
        self.priority = random.choice(priorityList)
        prefixList = ['ONLINE/ISSUES/ONELINER/',
                      'OFFLINE/ISSUES/ONELINER/',
                      'ONLINE/ISSUES/MULTILINER/',
                      'OFFLINE/ISSUES/MULTILINER/',
                      'ONLINE/DOCKER/ONELINER/',
                      'ONLINE/DOCKER/MULTILINER/']

        self.prefix = random.choice(prefixList)

    def execute(self):
        fullDetectionTime = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
        occurrence_time = fullDetectionTime[0:23] + 'Z'

        self.sendAlarm(occurrence_time, self.prefix + self.detectorName, self.priority, {'text': 'Test Alarm'})

if __name__ == '__main__':
    numberOfAlamrs = sys.argv[1]
    for i in range(numberOfAlamrs):
        myDetector = RandomAlarmGenerator()
        myDetector.execute()
