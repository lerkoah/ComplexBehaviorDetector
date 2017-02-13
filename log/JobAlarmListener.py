import os
import logging
import logstash
import pika
import json

def getIDs(raisedIDsPath):
    raisedIDs = open(raisedIDsPath, 'r')
    IDlist = raisedIDs.readlines()
    raisedIDs.close()
    return IDlist

def initializeLogger(host, port):
    logger = logging.getLogger('python-logstash-logger')
    logger.setLevel(logging.INFO)
    # test_logger.addHandler(logstash.LogstashHandler(host, 5001, version=1))
    logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))

    return logger

def sendToElastic(occurrence_time, name, priority, detectionTime, body):

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

def main():
    current_dir = os.path.dirname(os.path.realpath(__file__))

    ## Editable file
    raisedIDsPath = current_dir + '/raisedIDs.log'
    IDslist = getIDs(raisedIDsPath)

    ##RabbitMQ
    # Magic Numbers
    credentials = pika.PlainCredentials('alma', 'guest')
    host = 'ariadne.osf.alma.cl'
    port = 5672

    #Connection
    parameters = pika.ConnectionParameters(host, port, '/', credentials)
    connection = pika.BlockingConnection(parameters)

    #Creating channel
    channel = connection.channel()
    channel.queue_declare(queue='alarm')

    method_frame, header_frame, body = channel.basic_get(queue='alarm')
    while method_frame == None:
        method_frame, header_frame, body = channel.basic_get(queue='alarm')

    data = None
    if method_frame.NAME == 'Basic.GetEmpty':
        connection.close()
    else:
        channel.basic_ack(delivery_tag=method_frame.delivery_tag)
        connection.close()
        data = json.loads(body)

    raisedIDs = open(raisedIDsPath,'a')


    ## Compute the unique ID in unix format
    uniqueID = data['Name'] + '::'+ data['occurrence_time']

    ## If the error has never been raised
    ## then, raise the error.
    if not (uniqueID+'\n') in IDslist:
        ## Send to Elasticsearch the alarm
        sendToElastic(data['occurrence_time'],data['Name'],data['priority'],data['detection_time'], data['body'])
        raisedIDs.write(uniqueID + '\n')

    raisedIDs.close()

if __name__ == '__main__':
    main()