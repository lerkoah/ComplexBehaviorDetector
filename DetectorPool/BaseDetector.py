import pika
import json

class BaseDetector(object):
    def __init__(self,priority = 'DEBUG'):
        self.dectectorName = None
        self.report = 'Reporting alarm'
        self.priority = priority
        self.params = None
        ## error log path
        # self.errorLogPath = os.path.dirname(os.path.realpath(__file__)) + '/log/raisedAlarms.log'
        self.errorLogPath = '/home/lerko/ComplexBehaviorDetector/AlarmSystem/raisedAlarms.log'

        ## RabbitMQ Parameters

        # Magic Numbers
        credentials = pika.PlainCredentials('alma', 'guest')
        host = 'ariadne.osf.alma.cl'
        port = 5672
        self.alarmQueue = 'alarm'

        # Connecting
        parameters = pika.ConnectionParameters(host, port, '/', credentials)
        connection = pika.BlockingConnection(parameters)

        self.channel = connection.channel()
        self.channel.queue_declare(queue=self.alarmQueue)


    def configure(self,params):
        self.params = params
    def execute(self):
        if self.params == 1:
            return 0
        elif self.params == 0:
            return 0

    def sendAlarm(self, occurrence_time, name, priority, body):
        self.lastError= '=== START ERROR: ' + str(priority) + ' ===\n' \
                        '@timestamp: ' + str(occurrence_time) + '\n' + \
                        'Path: '+ str(name)+ '\n' \
                        'Priority: '+ str(priority) + '\n' \
                        'Body: '+ str(body) + '\n' \
                        '=== END ERROR ===\n'
        ## Printing in stdout
        print self.lastError

        ## Send to RabbitMQ
        jsonAlarm = json.dumps(self.__alarm2json(occurrence_time, name, priority, body))

        self.channel.basic_publish(exchange='',
                              routing_key=self.alarmQueue,
                              body=jsonAlarm,
                              properties=pika.BasicProperties(delivery_mode=2))

    def executeTruePositive(self):
        self.params = 0
    def executeTrueNegative(self):
        self.params = 1

    def __alarm2json(self, occurrence_time, name, priority, body):
        jsonFormat = {
            "@timestamp": occurrence_time,
            "path": name,
            "priority": priority,
            "body": body
        }
        return jsonFormat
