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

def sendToElastic(occurrence_time, name, priority, detectionTime, body):
    '''To send to elasticsearch as a json format'''
    host = 'ariadne.osf.alma.cl'
    port = 5003
    logger = initializeLogger(host,port)
    print '  - Sending log to Elasticsearch.'

    print '    - Initialization in %s:%s' % (host, port)
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

def processingAlarm(IDslist, raisedAlarms, body):
    '''Process the alarm from RabbitMQ.
    This function decide if the alarm must be raised or not.'''
    data = json.loads(body)
    ## Compute the unique ID in the appropriated format
    uniqueID = data['Name'] + '/'+ data['occurrence_time']

    # print 'Raised IDs: '+str(IDslist)
    # print 'Current ID: '+uniqueID

    ## If the error has never been raised
    ## then, raise the error.
    if not (uniqueID) in IDslist:
        ## Send to Elasticsearch the alarm
        sendToElastic(data['occurrence_time'],data['Name'],data['priority'],data['detection_time'], data['body'])

        error = '=== START ERROR: ' + str(data['priority']) + ' ===\n' \
                'Unique ID: ' + str(data['Name'])+'/'+data['occurrence_time'] + '\n' \
                'Occurrence Time: ' + str(data['occurrence_time']) + '\n' \
                'Detection Timestamp: ' + str(data['detection_time']) + '\n' \
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
    host = 'ariadne.osf.alma.cl'
    port = 5672

    ## Alarms control params
    # Editable file path and obtain the IDs
    raisedAlarmsPath = current_dir + '/raisedAlarms.log'
    IDslist = getIDs(raisedAlarmsPath)


    # Raised Alarms
    raisedAlarms = open(raisedAlarmsPath, 'a')

    #Connection as a Blocking Channel
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)

    #Creating channel
    channel = connection.channel()
    channel.queue_declare(queue='alarm')
    channel.basic_consume(processingAlarm, no_ack=True, queue='alarm')

    ## Obtaining alarms from RabbitMQ, the method basic_get()
    ## obtains a single message from the queue and return the
    ## param method that it is NoneType if the queue is empty.
    method, header, body = channel.basic_get(queue='alarm', no_ack=True)
    while not method == None:
        processingAlarm(IDslist, raisedAlarms, body)
        method, header, body = channel.basic_get(queue='alarm', no_ack=True)

    ## Close connections
    connection.close()
    raisedAlarms.close()

if __name__ == '__main__':
    tic = time.time()
    main()
    toc = time.time() - tic
    print 'Elapse: %s' % toc