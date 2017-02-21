class one_line_db():
    def __init__(self):
        self.names = ['ICT-5724', 'ICT-6207', 'ICT-5673',
                      'ICT-5343', 'ICT-3429', 'ICT-4841',
                      'ICT-7311', 'ICT-6195', 'ICT-3447',
                      'Operation: BLCORR System Restarts',
                      'ICT-4575', 'ICT-7303', 'ICT-2784',
                      'ICT-7566', 'NPE Scheduling', 'PRTSIR-9574',
                      'ICT-5354', 'ICT-6942']
        self.queries = ['("retrieving WVR temperatures" AND -"0)")  ("wvr event for ingested" AND -"1)") (CORR AND retrieve AND failed)',
                        '"Not found spectral data!!"',
                        'text: "failed to wait for blob"',
                        '"The total number of senders is" AND "gave up"',
                        'ACACORR AND "was busy.  -- retry" AND text: /[3-9][0-9]/',
                        '"Not found channel average data!!"',
                        '"startSend error"',
                        'St9bad_alloc AND TOTALPOWER',
                        '"startSubscanSequence handling unexpected exception"',
                        'text: "shutDownSubsysPass1"',
                        '"collector failed on unexpected hardware time stamp"',
                        '"create thread is failed!!." AND ACACORR',
                        '"start-time is in the past"',
                        'MountReaderThread AND "OBJECT_NOT_EXIST"',
                        'Process:SCHEDULING AND java.lang.NullPointerException AND !LogLevel:Debug AND !SourceObject:SCHEDULING_UPDATER AND !SourceObject:"Scheduling Standalone Array Panel" AND !text:findByEntityId AND !text:"startManualModeSession" AND !text:"alma.scheduling.array.executor.ManualRunningExecutionState.observe" AND !text:"alma.asdmIDLTypes.IDLEntityRefHelper.write"',
                        'text:"number of frames is different from what was expected "',
                        '"waiting for a dump timed out "',
                        '"failed to start flow transference" AND "TotalPowerDataFlow" AND LogLevel:ERROR AND Process:"CONTROL/ACC/TOTALPOWER/cppContainer"']
        self.priorities = len(self.names)*[0]
    def setDB(self,names,queries):
        self.names = names
        self.queries = queries
    def getQueries(self):
        return [list(tuple) for tuple in list(zip(self.names, self.queries, self.priorities))]