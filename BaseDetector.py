class BaseDetector(object):
    def __init__(self,priority = 'DEBUG'):
        self.dectectorName = None
        self.params = None
        self.report = 'Reporting alarm'
        self.priority = priority
        self.lastError = None
        ## error log path
        # self.errorLogPath = os.path.dirname(os.path.realpath(__file__)) + '/log/historical.log'
        self.errorLogPath = '/home/lerko/Desktop/ComplexBehaviorDetector/log/historical.log'

    def configure(self,params):
        self.params = params
    def execute(self):
        if self.params == 1:
            return 0
        elif self.params == 0:
            return 0

    def sendAlarm(self, occurrence_time, name, priority, detectionTime, body):
        self.lastError= '=== START ERROR: ' + str(priority) + ' ===\n' \
                        'Occurrence Time: ' + str(occurrence_time) + '\n' + \
                        'Detection Timestamp: '+ str(detectionTime) + '\n' \
                        'Name: '+ str(name)+ '\n' \
                        'Priority: '+ str(priority) + '\n' \
                        'Body: '+ str(body) + '\n' \
                        '=== END ERROR ===\n'
        ## Writting in editable file
        handler = open(self.errorLogPath, 'a')
        handler.write(self.lastError)
        handler.close()

        print self.lastError
        print self.__alarm2json(occurrence_time, name, priority, detectionTime, body)

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

    def __alarm2json(self, occurrence_time, name, priority, detectionTime, body):
        jsonFormat = '{' \
                     '"occurrence_time": %s, ' \
                     '"Name": %s, ' \
                     '"priority": %s, ' \
                     '"detection_time": %s, ' \
                     '"Body": %s' \
                     '}' %(occurrence_time, name, priority, detectionTime, body)
        return jsonFormat