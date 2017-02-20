import os
import logging
import logstash
import pika
import json
import time
from args import args
from conf import get_conf


global current_dir
current_dir = os.path.dirname(os.path.realpath(__file__))

def cleanOlderErrors(raisedIDsPath, maxNumberOfError = 1000):
    all_lines_arch = open(raisedIDsPath, 'r')
    all_lines = all_lines_arch.readlines()
    all_lines_arch.close()

    new_lines = open(raisedIDsPath,'w')
    clean_lines = []
    numberOfErrors = len([i for i,line in enumerate(all_lines) if '=== END ERROR ===' in line])

    if numberOfErrors > maxNumberOfError:
        counter = 0
        for line in reversed(all_lines):
            if '=== END ERROR ===' in line:
                counter += 1
            if counter > maxNumberOfError:
                new_lines.writelines(clean_lines)
                new_lines.close()
                return clean_lines
            if not line[-1] == '\n':
                line = line + '\n'
            clean_lines.insert(0,line)

    new_lines.writelines(all_lines)
    new_lines.close()
    return all_lines



def getIDs(raisedIDsPath):
    '''Get the raised ID as a list'''
    IDlist = []
    lines = cleanOlderErrors(raisedIDsPath)

    for line in lines:
        # print line
        if 'Unique ID: ' in line:
            IDlist.append(line[11:-1])

    return IDlist

def initializeLogger(host, port):
    '''Initialize the logger for send json to logstash'''
    logger = logging.getLogger('python-logstash-logger')
    logger.setLevel(logging.INFO)
    # test_logger.addHandler(logstash.LogstashHandler(host, 5001, version=1))
    logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))

    return logger

def sendToLogstash(logger, data):
    '''To send to elasticsearch as a json format'''
    print '  - Sending log to Logstash.'
    print '    - Creating data...',
    print 'done.'
    print '    - Sending data...',
    logger.info(str(data), extra=data)
    print 'done.'

def processingAlarm(IDslist, raisedAlarms, logger, body):
    '''Process the alarm from RabbitMQ.
    This function decide if the alarm must be raised or not.'''
    data = json.loads(body)
    # print data
    ## Compute the unique ID in the appropriated format
    uniqueID = str(data['path']) + '/'+ str(data['@timestamp'])

    # print 'Raised IDs: '+str(IDslist)
    # print 'Current ID: '+uniqueID

    ## If the error has never been raised
    ## then, raise the error.
    if not (uniqueID) in IDslist:
        ## Send to Elasticsearch the alarm
        sendToLogstash(logger, data)

        error = '=== START ERROR: ' + str(data['priority']) + ' ===\n' \
                'Unique ID: ' + str(data['path'])+'/'+data['@timestamp'] + '\n' \
                '@timestamp: ' + str(data['@timestamp']) + '\n' \
                'Name: ' + data['path'] + '\n' \
                'Priority: ' + str(data['priority']) + '\n' \
                'Body: ' + str(data['body']) + '\n' \
                '=== END ERROR ===\n'
        ## Printing in stdout
        print error
        ## Save the alarm
        raisedAlarms.write(error)
        IDslist.append(uniqueID)


def main():
    options = args()
    config = get_conf(options['config_file'])

    ##RabbitMQ
    # Magic Numbers
    credentials = pika.PlainCredentials(config['rabbitmq']['user'], config['rabbitmq']['pass'])
    rabbitMQHost, rabbitMQPort = config['rabbitmq']['hosts'][0].split(':')
    rabbitMQPort = int(rabbitMQPort)

    ##Logstash
    #Magic Numbers
    logstashHost, logstashPort = config['logstash']['hosts'][0].split(':')
    logstashPort = int(logstashPort)
    logger = initializeLogger(logstashHost, logstashPort)

    ## Alarms control params
    # Editable file path and obtain the IDs
    raisedAlarmsPath = current_dir + '/raisedAlarms.log'
    IDslist = getIDs(raisedAlarmsPath)


    # Raised Alarms
    raisedAlarms = open(raisedAlarmsPath, 'a')

    #Connection as a Blocking Channel
    parameters = pika.ConnectionParameters(rabbitMQHost, rabbitMQPort, '/', credentials)
    connection = pika.BlockingConnection(parameters)

    #Creating channel
    alarmQueue = 'alarm'
    channel = connection.channel()
    channel.queue_declare(queue=alarmQueue)

    for msg in channel.consume(no_ack=True, queue=alarmQueue, inactivity_timeout=1):
        # print msg
        if msg is None:
            break
        method, properties, body = msg
        processingAlarm(IDslist, raisedAlarms, logger, body)
        # print IDslist

    ## Close connections
    connection.close()
    raisedAlarms.close()

if __name__ == '__main__':
    tic = time.time()
    main()
    toc = time.time() - tic
    print 'Elapse: %s' % toc
