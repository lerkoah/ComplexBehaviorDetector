#! /usr/bin/env python
"""
======================================================================
LogQuery : abstraction for ALMA ElasticSearch stack
VERSION     : 1.0  -  FEBRUARY, 2017
======================================================================
Requirements: 
* elasticsearch-dsl

Available in pip for Python 2.7 and Python 3.5
pip install elasticsearch-dsl

You should execute this import wihout errors:
>>> import elasticsearch_dsl


This utility is intended to be run in command line, so despite doctests 
are already in place when using --unittest flag, higher level testing
must be done in bash. Try these examples:

Help
$ LogQuery -h

Long and short options
$ LogQuery --index online --verbose --limit 5 --fromTime 2017-01-30T00:00:00.000 --toTime 2017-01-30T01:00:00.000 "*" 
$ LogQuery -i online -v -l 5 -f 2017-01-30T00:00:00.000 -t 2017-01-30T01:00:00.000 "*" 

Environment vars could be used instead of parameters. The following shortcuts are available:

    LQ_INDEX
    LQ_ORIGIN
    LQ_FROMTIME
    LQ_TOTIME
    LQ_LOGLEVEL
    LQ_LIMIT
    LQ_FORMAT
    LQ_COLUMNS

$ export LQ_FROMTIME=2017-01-30T00:00:00.000
$ export LQ_TOTIME=2017-01-30T10:00:00.000
$ export LQ_INDEX=online
$ export LQ_LIMIT=5
$ LogQuery -v '*'

The following examples assumes that you alread exported the previous ENV values.
Of course, you can use the parameters instead of ENV vars. 

Query options examples:
$ LogQuery --reverse "*" 
$ LogQuery --stats "*" 
$ LogQuery --origin TFINT --loglevel DEBUG '*'

Output options examples:
$ LogQuery --columns "@timestamp,origin,LogLevel,Process,SourceObject,text" '*'
$ LogQuery -v --format "{@timestamp} {LogLevel} [{SourceObject}] {text}" '"CONTROL/DV01"'

Typical query
$ export LQ_LOGLEVEL=INFO
$ export LQ_COLUMNS=TimeStamp,LogLevel,Process,SourceObject,text,Data.text 
$ LogQuery --limit 200 'Process: "CONTROL/ACC/javaContainer"' -v -f "2017-01-30T09:15:00.000"


Fancy options:
$ LogQuery --extrahelp  # This same doc
$ LogQuery --unittest  # Wants verbosity? -v

More documentation and examples at https://ictwiki.alma.cl/twiki/bin/view/SoftOps/LogQuery
Any doubt, please send an email to juan.gil@alma.cl or read ICT-9000
======================================================================
Pending issues:
1) Check invalid indices.
TimeUtils(prefix="invalid", fr="2017-01-30T00:00:00.000", to="2017-01-31T00:00:00.000").getIndices()

2) Enable dot notation: 
$ LogQuery --columns TimeStamp,LogLevel,Process,SourceObject,text,Data.text "*" 
======================================================================
"""

import sys, copy, os, unittest, re, argparse
from datetime import datetime
from time import mktime, strptime
#from time import strftime, gmtime
import doctest
import pytz

# import elasticsearch_dsl
# from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.query import Query


################################################
# MAGIC NUMBERS!!!
# This MUST be taken elsewhere. But in the sake 
# of simplicity, please don't use YAML.
################################################
ALMAELKHOST          =["http://elk-master.osf.alma.cl:9200", "http://elk-master2.osf.alma.cl:9200"]
QUERYRESULTS_MAX     =10000
QUERYRESULTS_DEFAULT =1000
QUERY_TIMEOUT        =300 #seconds
INDEX_PREFIX         ="online"



################################################
# Function and clases
################################################
# Log levels

L_QUIET, L_ERRORS, L_NORMAL, L_VERBOSE, L_DEBUG = (0,1,2,3,4)
VERBOSITY = L_QUIET

def inColor(color):
    return lambda txt: color + str(txt) + '\033[0m'

def log(loglevel, txt):
    if VERBOSITY >= loglevel:
        if loglevel == L_VERBOSE:
            print (inColor('\033[32m')(txt)) # green
        elif loglevel == L_DEBUG:
            print (inColor('\033[33m')(txt)) # yellow
        elif loglevel == L_ERRORS:
            print (inColor('\033[34m')(txt)) # red
        elif loglevel == L_NORMAL:
            print (txt)

class TimeUtils:
    """
    Helper class to transform date ranges to indices

    ElasticSearch don't allow to infer index names from timestamps in filters.
    https://www.elastic.co/guide/en/elasticsearch/reference/current/date-math-index-names.html

    Test cases
    >>> t1 = TimeUtils(prefix="online", fr="2017-01-30T00:00:00.000", to="2017-01-29T00:00:00.000")
    Traceback (most recent call last):
    ...
    ValueError: fr must be lesser than to

    """
    def __init__(self, prefix="", fr="", to="", reverse=False):
        # if fr == "" or to == "" :
        #     raise ValueError('fr and to are required values')

        if fr != "":
            self.fr = self.toMillis(fr)
            self.frZ = fr+"Z"

        if to != "":
            self.to = self.toMillis(to)
            self.toZ = to+"Z"

        if fr and to and self.fr >= self.to:
            raise ValueError('fr must be lesser than to')

        self.prefix = prefix
        self.reverse = reverse


    def toMillis(self, string):
        """
        TODO: Fix UTC for chilean machines.
        #>>> tu=TimeUtils(prefix="online", fr="2017-01-30T00:00:00.000", to="2017-01-30T00:00:00.000")
        #>>> tu.toMillis("2016-10-20T00:00:00.123")
        1476932400123

        #>>> tu.toMillis("2016-10-20")
        1476932400000
        """
        T = (str(string) + "00000000000000000000000")[0:23]
        T = T[0:4]+"-"+T[5:7]+"-"+T[8:10]+"T"+T[11:13]+":"+T[14:16]+":"+T[17:19]+"."+T[20:23]
        # datetime.datetime is not compatible with Python 2.7
        # return int(1000*datetime.datetime(int(T[0:4]) , int(T[5:7]), int(T[8:10]), int(T[11:13]), int(T[14:16]), int(T[17:19]), int(T[20:23])*1000).timestamp())
        return int( mktime( strptime(T[0:19], "%Y-%m-%dT%H:%M:%S") )*1000 + int(T[20:23]) )

    def getIndices(self, prefix=""):
        """
        >>> TimeUtils(prefix="online", fr="2016-10-20T00:00:00.000", to="2016-10-23T00:00:00.000").getIndices()
        ['online-2016.10.20', 'online-2016.10.21', 'online-2016.10.22', 'online-2016.10.23']

        >>> TimeUtils(prefix="online", fr="2016-10-20T00:00:00.000", to="2016-10-23T00:00:00.000", reverse=True).getIndices()
        ['online-2016.10.23', 'online-2016.10.22', 'online-2016.10.21', 'online-2016.10.20']

        >>> TimeUtils(prefix="online", fr="2016-10-20T00:00:00.000", to="2016-10-20T00:00:01.000").getIndices()
        ['online-2016.10.20']

        >>> TimeUtils(prefix="online", fr="2016-10-19T23:00:00.000", to="2016-10-20T00:00:01.000").getIndices()
        ['online-2016.10.19', 'online-2016.10.20']

        >>> TimeUtils(fr="2016-10-19T01:00:00.000", to="2016-10-20T23:00:01.000").getIndices(prefix="online")
        ['online-2016.10.19', 'online-2016.10.20']
        """
        def toDate(milliTimeEpoch):
            # See http://stackoverflow.com/questions/3694487/initialize-a-datetime-object-with-seconds-since-epoch
            # try: # Python 3
                return str(datetime.fromtimestamp(milliTimeEpoch /1000.0))[0:10].replace("-", ".")
            # except: # Python 2
                return str(datetime.fromtimestamp(milliTimeEpoch /1000.0, pytz.utc))
                #return strftime( "%Y.%m.%d", gmtime( milliTimeEpoch / 1000 ) )
        oneDay = 1000*60*60*24

        if prefix == "":
            prefix = self.prefix

        now = self.fr
        indices = []
        indices.append(prefix+"-"+toDate(now))
        while (toDate(now) != toDate(self.to)):
            now = now + oneDay
            indices.append(prefix+"-"+toDate(now))
        # indices

        if self.reverse:
            indices.reverse()

        log(L_DEBUG, "INDICES: %s" % indices)
        return indices



def fill_args_from_env():
    """
    Use environment variables as an alternative to command line parameters

    sys.argv is filled with LQ_something only if it is not defined. For example:

    1) Add --index online
    2) Ignore loglevel if long param already given in sys.argv
    3) Ignore loglevel if short param already given in sys.argv

    >>> sys.argv = ['LogQuery', '--loglevel', 'INFO', '-t', '123']
    >>> os.environ["LQ_INDEX"] = "online"
    >>> os.environ["LQ_LOGLEVEL"] = "DEBUG"
    >>> os.environ["LQ_TOTIME"] = "456"
    >>> os.environ["LQ_DEBUG"] = "1"

    >>> fill_args_from_env()

    >>> "--index" in sys.argv
    True
    >>> "online" in sys.argv
    True
    >>> "DEBUG" not in sys.argv
    True
    >>> "INFO" in sys.argv
    True
    >>> "456" not in sys.argv
    True
    >>> "123" in sys.argv
    True
    >>> "--debug" in sys.argv
    True
    """
    for param in [("i", "index"), ("f", "fromTime"), ("t", "toTime"), ("g", "loglevel"), 
        ("l", "limit"), ("g", "format"), ("debug", "debug"), ("c", "columns"), ("o", "origin")]:
        env = "LQ_"+param[1].upper()
        if "--"+param[1] not in sys.argv and "-"+param[0] not in sys.argv and env in os.environ.keys():
            # True only params
            if  param[1] in ["debug"]:
                sys.argv.append("--"+param[1])
            # Param: value
            else:
                sys.argv.append("--"+param[1])
                sys.argv.append(os.environ[env])

# Types, shared with cmdParser and SearchAlmaElk
def limit_type(string):
    value = int(string)
    if value<1 or value>QUERYRESULTS_MAX:
        msg = "%s is out of range. Must be in [1,%d]" % (string, QUERYRESULTS_MAX)
        raise argparse.ArgumentTypeError(msg)
    return value

def index_type(string):
    if not re.search("^([a-zA-Z0-9])*$", string):
        msg = "Not a valid index name. use just letters and numbers."
        raise argparse.ArgumentTypeError(msg)
    return string

def columns_type(string):
    string = str(string)
    if string != "" and not re.search("^([a-zA-Z0-9,@\.])*$", string):
        msg = "%r is not a valid list of columns. \nValid Example: --columns @timestamp,LogLevel,Process,Text,Data.text." % (string)
        raise argparse.ArgumentTypeError(msg)
    return string

def date_type(string):
    return string

def loglevel_type(string):
    return string.lower()

def query_type(string):
    if string == "":
        msg = "Enter a query."
        raise argparse.ArgumentTypeError(msg)
    return string


def cmdParser():
    global VERBOSITY # Ah, ugly. But simple.

    fill_args_from_env()

    if "--extrahelp" in sys.argv:
        print(__doc__)
        sys.exit()

    parser = argparse.ArgumentParser(
        description="Query ElasticSearch as they do in Kibana. This command line requires Python 2.7 and it is forward compatible with Python 3." ,
        epilog="Those options can also be set as ENV vars. More documentation and examples at https://ictwiki.alma.cl/twiki/bin/view/SoftOps/LogQuery. Also, try LogQuery --extrahelp"
       )


    parser.add_argument("--extrahelp", action="store_true", help="Display __doc__ with *extra* help.")
    parser.add_argument("--unittest", action="store_true", help="Run unit tests and exit.")

    # args = parser.parse_known_args()
    # print( args )

    parser.add_argument("query", type=query_type, help="query string as written in Kibana.")

    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose mode.")
    parser.add_argument("--debug", action="store_true", help="Debug mode. Spam in your screen.")
    parser.add_argument("--elastic-hosts", action="append", help="Hostname for ALMA-ELK ElasticSearch instance. Defaults to production ALMA-ELK")


    group = parser.add_argument_group("Query options")
    group.add_argument("-i", "--index", type=index_type, default=INDEX_PREFIX, help="Index prefix to query. Default: %s" % INDEX_PREFIX)
    group.add_argument("-o", "--origin", default="", help="Origin (APE1, AOS62, etc)")
    group.add_argument("-f", "--fromTime", required=True, type=date_type, help="From timestamp. See below for more details.")
    group.add_argument("-t", "--toTime", type=date_type, help="To timestamp. Defaults to now(). See below for more details.")
    group.add_argument("-g", "--loglevel", type=loglevel_type, choices=SearchAlmaELK.levels, default="", help="Minimum loglevel to return.")
    group.add_argument("-l", "--limit", default=1000, type=limit_type, help="Max size of result set. Defaults to %d." % QUERYRESULTS_DEFAULT)
    group.add_argument("-r", "--reverse", action="store_true", help="Reverse results, from older to newer")

    group = parser.add_argument_group("Output options")
    group.add_argument("-c", "--columns", type=columns_type, default="", help="Restrict output to certain columns, space separated.")
    # group.add_argument("-d", "--format", choices=['csv', 'json', 'container'], default="csv", help="Format to display returned data. Note that container overrides -c")
    group.add_argument("-d", "--format", default="", help="Format result using print 'FORMAT'.format(**hit)")
    group.add_argument("--stats", action="store_true", help="Display query statistics at the end")

    args = parser.parse_args()
    if args.debug:
        VERBOSITY = L_DEBUG
    elif args.verbose:
        VERBOSITY = L_VERBOSE

    # QUERY mode.
    # if args.query == "":
    #     parser.exit(1, "Please enter your query.\n" + parser.format_usage())

    if args.elastic_hosts is None:
        log(L_DEBUG, "Adding default elastic-host")
        args.elastic_hosts = ALMAELKHOST

    return parser, args


class SearchAlmaELK:
    """
    This class is the link between Elasticsearch logic and ALMA logs logic.

    >>> #levels = ['trace', 'delouse', 'debug', 'notice', 'info', 'warning', 'error', 'critical', 'emergency']
    >>> #levels[ levels.index('debug'): ]

    """
    levels = ['trace', 'delouse', 'debug', 'notice', 'info', 'warning', 'error', 'critical', 'emergency']
    def __init__(self, index, fromTime, toTime, query, limit, reverse=False, loglevel="", columns="", origin=""):
        """
        >>> isinstance(SearchAlmaELK( index="online", fromTime="2016-10-25T00", toTime="2016-10-25T10", query="*", limit=1 ), SearchAlmaELK)
        True
        >>> SearchAlmaELK( index="online", fromTime="2016-10-26T00", toTime="2016-10-25T10", query="*", limit=1 )
        Traceback (most recent call last):
        ...
        ValueError: fr must be lesser than to
        """
        self.time = TimeUtils(prefix=index, fr=fromTime, to=toTime, reverse=reverse)
        self.query = query_type(query)
        self.loglevel = loglevel.lower()
        self.limit = limit_type(limit)
        self.origin = origin
        if columns == "":
            self.columns = []
        else:
            self.columns = columns_type(columns).split(",")
        log(L_DEBUG, "Columns: " % self.columns)

        # self.Search = Search(index=self.time.getIndices()).from_dict( self.firstQueryDict() )
        s = Search(index=self.time.getIndices())
        s = s.sort( {"@timestamp":  {
                        "order": ["asc", "desc"][int(self.time.reverse)],  # True => desc
                        "unmapped_type": "boolean"
                      } } )

        s = s.filter( {"range" : { "@timestamp": {
                                  "gte": self.time.frZ,
                                  "lte": self.time.toZ,
                                  "format": "date_time"
                                } }} )
        s = s.query( "query_string", query=self.query, analyze_wildcard=True )

        for lvl in self.getLogLevelFilters(loglevel.lower()):
            s = s.query( ~Q( "match", LogLevel=lvl) )

        if origin != "":
            s = s.query( Q( "match", origin=origin ) )

        self.Search = s



    def getLogLevelFilters(self, l):
        """
        This function gives a list to filter out in elasticearch. For example:

        >>> sInst=SearchAlmaELK( index="online", fromTime="2016-10-25T00", toTime="2016-10-25T10", query="*", limit=1)
        >>> sInst.getLogLevelFilters( "debug" )
        ['trace', 'delouse']

        >>> sInst.getLogLevelFilters( "emergency" )
        ['trace', 'delouse', 'debug', 'notice', 'info', 'warning', 'error', 'critical']

        >>> sInst.getLogLevelFilters( "trace" )
        []
        """
        if l != "":
            return self.levels[ :self.levels.index(l) ]
        else:
            return []



    def to_dict(self):
        return self.Search.to_dict()

    def filter(self, Qobj):
        """
        >>> sInst=SearchAlmaELK( index="online", fromTime="2016-10-25T00", toTime="2016-10-25T10", query="*", limit=1)
        >>> sInst.filter( None )
        Traceback (most recent call last):
        ...
        TypeError: Parameter must be of type elasticsearch_dsl.Query
        """
        if not isinstance(Qobj, Query):
            msg = "Parameter must be of type elasticsearch_dsl.Query"
            raise TypeError(msg)

        self.Search = self.Search.filter(Qobj)
        return self


    def execute(self):
        return self.Search[0:self.limit].execute()

    def format(self, hit, format=""):
        """
        >>> sInst=SearchAlmaELK( index="online", fromTime="2016-10-25T00", toTime="2016-10-25T10",  \
              query="*", limit=1, columns="@timestamp,LogLevel,Process,text")
        >>> hit={'@version': '1', 'LogLevel': 'Warning', '@timestamp': '2016-10-25T04:41:59.161Z', \
          'text': 'Alarm already active: Fault State OFLS-ZR_SIGLOSS:ZR_SIGLOSS:2 discarded',      \
          'Thread': 'com.cosylab.acs.laser.AlarmSourcesListenerCached', 'Process': 'AlarmService', \
          'Host': 'gas05', 'StackLevel': '0', 'File': 'AlarmMessageProcessorImpl.java',            \
          'LogId': '124699', 'Routine': 'processChange', 'TimeStamp': '2016-10-25T04:41:59.161',   \
          'StackId': 'unknown', 'tags': ['APE1'], 'SourceObject': 'AlarmService', 'Line': '317'}
        >>> sInst.format( hit )
        '2016-10-25T04:41:59.161Z Warning AlarmService Alarm already active: Fault State OFLS-ZR_SIGLOSS:ZR_SIGLOSS:2 discarded'

        >>> sInst.format( hit, format='{TimeStamp} {LogLevel} [{SourceObject}] {text}'  )
        '2016-10-25T04:41:59.161 Warning [AlarmService] Alarm already active: Fault State OFLS-ZR_SIGLOSS:ZR_SIGLOSS:2 discarded'

        TODO
        # >>> sInst.format( hit, format='{TimeStamp} {LogLevel} [{SourceObject}] {text} {Data.text}'  )

        """
        if format != "":
            log(L_DEBUG, "Format given for hit: %s" % format)
            try:
                return format.format(**hit)
            except:
                raise NotImplemented
        elif len(self.columns) == 0:
            log(L_DEBUG, "format empty. Return hit as is.")
            return hit
        else:
            log(L_DEBUG, "Format given by columns: %s" % self.columns)
            result = []
            for col in self.columns:
                if col in hit.keys():
                    result.append(hit[col])
            return " ".join(result)



def main():
        # Normal operation
        parser, args = cmdParser()

        
        log(L_DEBUG, "ARGUMENTS: %s" % args)

        # I keep connection outside the classes, they should be called by itself
        log(L_VERBOSE, "---- Connecting to %s ..." % args.elastic_hosts)
        connections.create_connection(hosts=args.elastic_hosts, timeout=QUERY_TIMEOUT)
        log(L_DEBUG, "CONNECTION HEALTH: %s" % connections.get_connection().cluster.health())
        log(L_VERBOSE, "Cluster Status: %s " % connections.get_connection().cluster.health()['status'] )
        log(L_VERBOSE, "Min LogLevel  : %s" % args.loglevel)
        log(L_VERBOSE, "Starting query... please wait up to %s seconds" % QUERY_TIMEOUT)

        # t = TimeUtils(prefix=args.index, fr=args.fromTime, to=args.toTime, reverse=args.reverse)
        # log(L_DEBUG, indices)

        searchInstance = SearchAlmaELK( 
                index=args.index, 
                fromTime=args.fromTime, 
                toTime=args.toTime, 
                reverse=args.reverse, 
                loglevel=args.loglevel,
                limit=args.limit,
                columns=args.columns,
                query=args.query,
                origin=args.origin
            )

        log(L_DEBUG, "SEARCHINSTANCE: %s" % searchInstance.to_dict())
        response = searchInstance.execute()

        if not args.stats:
            log(L_VERBOSE, "---- Results ----")
            for hit in response.hits:
                print( searchInstance.format(hit.to_dict(), args.format) )

            log(L_VERBOSE, "---- Stats ----")
            log(L_VERBOSE, "Response took: %d ms" % response.took)
            log(L_VERBOSE, "Total hits: %d" % response.hits.total)
            if response.hits.total > args.limit:
                log(L_VERBOSE, "Results cropped at %d because --limit parameter was set (maybe implicitly)." % args.limit)
        else:
            print("Response took: %d ms" % response.took)
            print("Total hits: %d" % response.hits.total)


    


################################################
# Command line usage
################################################
if __name__ == '__main__':

    # Go to UNITTESTING
    if "--unittest" in sys.argv:
        doctest.testmod()

    # Normal mode
    else:
        main()


