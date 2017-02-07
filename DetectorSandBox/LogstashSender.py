import logging
import logstash

print 'Sending log to Elasticsearch.'
host = 'ariadne.osf.alma.cl'
port = 5001
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
# test_logger.addHandler(logstash.LogstashHandler(host, 5001, version=1))
test_logger.addHandler(logstash.TCPLogstashHandler(host, port, version=1))
print '  - Initialization in %s:%s' %(host,port)
print '  - Creating data...',

# add extra field to logstash message
occurrence_time = "2017-02-01T05:20:33.280Z"
name = "ICT-5354"
priority = "INFO"
detectionTime = "2017-02-06T15:13:33.271Z"
body = {
             "Context" : "",
        "SourceObject" : "ACACORR/CDPCIF/NODE_09",
              "origin" : "APE1",
             "Process" : "ACACORR/CDPC_DATA_MGR/N09/cppContainer",
                "Host" : "coj-cpn-009",
             "Routine" : "",
            "LogLevel" : "Error",
              "Thread" : "ACACDPC_PRE_INTEG_THREAD",
                "Line" : "151",
          "@timestamp" : "2017-02-01T05:20:33.280Z",
                "text" : "waiting for a dump timed out (last dump counter: 7708768) [ACACDPCPreIntegThread.cpp/151/virtual void ACACDPCPreIntegThread::run()]",
                "File" : "ACACDPCPreIlerkontegThread.cpp",
          "StackLevel" : "0",
             "StackId" : ""
    }

mylog = {
            "occurrence_time": occurrence_time,
            "Name": name,
            "priority": priority,
            "detection_time": detectionTime,
            "Body": body
        }
print 'done.'
print '  - Sending data...',
test_logger.info(str(mylog), extra =  mylog)
print 'done.'
