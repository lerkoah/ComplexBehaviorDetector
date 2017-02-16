import os
import logging
import logstash
import pika
import json
import time

global current_dir
current_dir = os.path.dirname(os.path.realpath(__file__))

def getIDs(raisedIDsPath):
    '''Get the raised ID as a list'''
    raisedIDs = open(raisedIDsPath, 'r')
    IDlist = []
    lines = raisedIDs.readlines()

    for line in lines:
        # print line
        if 'Unique ID: ' in line:
            IDlist.append(line[11:-1])

    raisedIDs.close()
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
    uniqueID = str(data['Name']) + '/'+ str(data['@timestamp'])

    # print 'Raised IDs: '+str(IDslist)
    # print 'Current ID: '+uniqueID

    ## If the error has never been raised
    ## then, raise the error.
    if not (uniqueID) in IDslist:
        ## Send to Elasticsearch the alarm
        sendToLogstash(logger, data)

        error = '=== START ERROR: ' + str(data['priority']) + ' ===\n' \
                'Unique ID: ' + str(data['Name'])+'/'+data['@timestamp'] + '\n' \
                '@timestamp: ' + str(data['@timestamp']) + '\n' \
                'Name: ' + data['Name'] + '\n' \
                'Priority: ' + str(data['priority']) + '\n' \
                'Body: ' + str(data['body']) + '\n' \
                '=== END ERROR ===\n'
        ## Printing in stdout
        print error
        ## Save the alarm
        raisedAlarms.write(error)
        IDslist.append(uniqueID)


def main():
    ##RabbitMQ
    # Magic Numbers
    credentials = pika.PlainCredentials('alma', 'guest')
    rabbitMQHost = 'ariadne.osf.alma.cl'
    rabbitMQPort = 5672

    ##Logstash
    #Magic Numbers
    logstashHost = 'ariadne.osf.alma.cl'
    logstashPort = 5003
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
        print IDslist

    ## Close connections
    connection.close()
    raisedAlarms.close()

if __name__ == '__main__':
    tic = time.time()
    main()
    toc = time.time() - tic
    print 'Elapse: %s' % toc