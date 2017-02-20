---
author: Lerko Araya Hernández
title: "Alarm System Documentation"
date: "2017-02-17 14:23"
---
# Alarm System based on Jenkins
This is the complete documentation about the Alarm System based on Jenkins. The main features of this system are the capacity for send alarms to elasticsearch using logstash and visualize them in a dashboard. Also, we use jenkins for send important mails.

## Overview
The full system comprise the alarm notification and visualization, it is implies to send an alarm to elasticsearch using logstash and finally send a email with to alert the respective team. Also, we save an historical alarm file named ```raisedAlarms.log```.

The first module aim to send an alarm to elasticsearch and save the raised alarm in the historical file. This module named ```Alarm Selector```. Then, the second one attendant to send mails using Jenkins templates. This module named ```Alarm Summary Mail Sender```.

![Full System](fullsystem.png)
Reminding, the figure shows the full system including the Job Manager. The Alarm Selector pulls the alarms from RabbitMQ. Then, the Mail Sender makes a query to elasticsearch for send emails.

## Alarm Selector
The Alarm Selector intizalize credentials. For make this we uncoupled the servers and ports directions. These are in a config file that we passed using the command line. The usage is:

```command
python /path/to/AlarmSelector.py -c /path/to/config.json
```

For example:

```command
python /home/lerko/ComplexBehaviorDetector/AlarmSystem/AlarmSelector.py -c /home/lerko/ComplexBehaviorDetector/AlarmSystem/config.json
```

Then we Initialize credentials using the functions ```args()``` and ```get_conf()```.
```python
def main():
    options = args()
    config = get_conf(options['config_file'])

    ##RabbitMQ
    # Magic Numbers
    credentials = pika.PlainCredentials('alma', 'guest')
    rabbitMQHost, rabbitMQPort = config['rabbitmq']['hosts'][0].split(':')
    rabbitMQPort = int(rabbitMQPort)

    ##Logstash
    #Magic Numbers
    logstashHost, logstashPort = config['logstash']['hosts'][0].split(':')
    logstashPort = int(logstashPort)
    logger = initializeLogger(logstashHost, logstashPort)
```
Then, we load the raised IDs, this IDs are a combination of fields path and @timestamp. The function ```getIDs()``` was designed for load the corresponding IDs from the historical raised alarms file.
```python
    ## Alarms control params
    # Editable file path and obtain the IDs
    raisedAlarmsPath = current_dir + '/raisedAlarms.log'
    IDslist = getIDs(raisedAlarmsPath)


    # Raised Alarms
    raisedAlarms = open(raisedAlarmsPath, 'a')
```

Finally, we want to pull the alarms from RabbitMQ.  For this work, we use the ```pika``` python library.

```python
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
```
For close the program, please do not forget close all connections and files.
```python
    ## Close connections
    connection.close()
    raisedAlarms.close()
  ```

## Alarm Summary Mail Sender
The email sender is based on the *Email Extension Template Plugin* of Jenkins. This plugins offer the possibility of raise alarms if an regular expression appears in the Jenkins standard output.

The module was made by Marcelo Jara. The philosophy behind this module is create a **Bucket** for recollect the interesting data. Each *bucket* attempt to and specific type of log. For example, the ```PrefixBucket()``` search an specific prefix in the field ```path```.

The usage of this module is the following:

```command
usage: main.py [-h] [-l LAST] [-f FROM_TIME] [-t TO_TIME] [-c CONFIG]
               [-p MIN_PRIORITY]
               query

positional arguments:
  query                 Query string as written in Kibana.

optional arguments:
  -h, --help            show this help message and exit
  -l LAST, --last LAST  Time to query ES for last logs, overrides from/to.
                        Example: 1s, 1m, 2h, 3d, 5w
  -f FROM_TIME, --from-time FROM_TIME
                        Time lower limit in UTC
  -t TO_TIME, --to-time TO_TIME
                        Time upper limit in UTC
  -c CONFIG, --config CONFIG
                        Config file path
  -p MIN_PRIORITY, --min-priority MIN_PRIORITY
                        Minimum priority to fetch.
```
