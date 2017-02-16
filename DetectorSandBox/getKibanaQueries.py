# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 17:41:25 2017

@author: epikt
"""
import re
from JIRAManager import TicketManager



def get_kibana_query(description):
    """Extract the kibana query from a ticket description"""
    m=re.search("(?<={code:title=Kibana}).*\n.*\n.*?{code}",description)
#    (?<=...)
    #print description
    if m:   # if m is not NoneType, that is, we get a match
        query=m.group(0)  # we're assuming there is only 1 match
        # at this point we have something like 
        # "some stuff"\r\n{code}'". We need to clean it
        query=query[0:query.find('{code}')].strip()
        return query
        
    else:
        return None

def getQueries():
    kibana_queries=[]

    # get an instance of JIRA TicketManager
    # Using 'TEST' will use http://jiradev01.sco.alma.cl server, use ICT for production
    jira=TicketManager("jreveco","jira4test","TEST")
    #jira=TicketManager("software","<softwarepass>","ICT")

    # get a dictionary with the list of issues matching the JQL query
    issues_list=jira.find_issues('Description ~"code:title=Kibana" AND status not in (Resolved,Closed)')
    # since the simple 'get_issue' method from TicketManager doesn't retrieve the description of the ticket
    # we'll use the more advanced 'get_issue_json' method which extracts all the ticket information

    # first, we iterate throug the list
    for issue in issues_list:
        # get the issue json
        issue_json=jira.get_issue_json(issue)
        # get the description
        description=issue_json['fields']['description']
        # now we get the kibana query, if we cannot get it, we print a message
        # (that could be replaced by raising an exception)
        kibana_query=get_kibana_query(description)
        if kibana_query:  # if we found a kibana query, we add it to the list
            kibana_queries.append([issue,kibana_query.strip()])
        else:
            raise Exception("No queries were found for %s"%issue)

    # this can be returned
    # for name,query in kibana_queries:
    #     print 'ICT Name: ' + name
    #     print 'Query   : ' + query
    return kibana_queries

print getQueries()