import logging
import logstash

class BaseDetector(object):
    def __init__(self,priority = 'DEBUG'):
        self.dectectorName = None
        self.report = 'Reporting alarm'
        self.priority = priority
        self.params = None
        ## error log path
        # self.errorLogPath = os.path.dirname(os.path.realpath(__file__)) + '/log/historical.log'
        self.errorLogPath = '/home/lerko/Desktop/ComplexBehaviorDetector/log/historical.log'

        self.host = 'ariadne.osf.alma.cl'
        self.port = 5001
        self.logger = self.__initializeLogger(self.host, self.port)

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

        # self.__sendToElastic(self.logger,occurrence_time, name, priority, detectionTime, body)

        print self.lastError
        print self.__alarm2json(occurrence_time, name, priority, detectionTime, body)

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

    def __initializeLogger(self, host, port):
        logger = logging.getLogger('python-logstash-logger')
        logger.setLevel(logging.INFO)
        # test_logger.addHandler(logstash.LogstashHandler(host, 5001, version=1))
        logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))

        return logger
    def __alarm2json(self, occurrence_time, name, priority, detectionTime, body):
        jsonFormat = {
            "occurrence_time": occurrence_time,
            "Name": name,
            "priority": priority,
            "detection_time": detectionTime,
            "Body": body
        }
        return jsonFormat

    def __sendToElastic(self, logger, occurrence_time, name, priority, detectionTime, body):
        print '  - Sending log to Elasticsearch.'

        print '    - Initialization in %s:%s' % (self.host, self.port)
        print '    - Creating data...',

        mylog = {
            "occurrence_time": occurrence_time,
            "Name": name,
            "priority": priority,
            "detection_time": detectionTime,
            "Body": body
        }
        print 'done.'
        print '    - Sending data...',
        logger.info(str(mylog), extra=mylog)
        print 'done.'