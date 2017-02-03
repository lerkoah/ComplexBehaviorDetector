#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import traceback 
import requests
import logging


logger = logging.getLogger("__JIRATicketsManager__")

# For comodity, I'm defining here some default info
url_jira='http://jira.alma.cl'
url_ict_jira='http://ictjira.alma.cl'
def convert_to_ascii(input):
    if input == None:
        return None
    if isinstance(input, dict):
        return dict((convert_to_ascii(key), convert_to_ascii(value)) for key, value in input.iteritems())
    elif isinstance(input, list):
        return [convert_to_ascii(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('ascii','ignore')
    else:
        return input

class TicketManager:
    """Class to retrieve tickets from jira"""    
    def __init__(self,username,password,server):
        """Receives as parameter the username, password and server. As server us 'ICT' or 'JIRA'"""
        if server == "ICT":
            self.baseURL='http://ictjira.alma.cl'
        elif server == "JIRA":
            self.baseURL='http://jira.alma.cl'
        elif server == "TEST":
            self.baseURL='http://jiradev01.sco.alma.cl'  
        else:
            print "Unknown server, please use 'ICT' or 'JIRA'"
            return
        self.version="latest"
        self.session=requests.Session()
        # the following line gets a session
        r=self.session.get(self.baseURL+'/rest/auth/1/session',auth=(username, password))
        if r.status_code != 200:
            print "There was a problem connecting to JIRA, this fetcher will not work"
            print r.text
    def get_issue(self,key):
        """ Given an issue key (i.e. ICT-9, AIV-22) returns its [summary, status, assignee,issue_type]"""
        issue=convert_to_ascii(self.get_issue_json(key))      
        if issue == None:
            return [None,None,None,None]
        else:
            summary=issue['fields']['summary']
            assignee=issue['fields']['assignee']['name']
            status=issue['fields']['status']['name']
            issue_type=issue['fields']['issuetype']['name']
            return [summary,status,assignee,issue_type]
            
    def get_issue_json(self,key):
        """Given an issue key (i.e. ICT-9, AIV-22) returns its json description. 
        Beware the json description will depend on the JIRA version """
        try:
            response = self.session.get(self.baseURL+'/rest/api/%s/issue/%s' % (self.version,key))
            if response.status_code == 200:
                # Not all resources will return 200 on success. 
                issue = convert_to_ascii(response.json())
                return issue
            else:
                return None
        except Exception:
            print "Error fetching issue: "+key
            print str(traceback.format_exc())
            return None
            
    def get_issue_remotelinks(self,key):
        """ Given an issue key (i.e. ICT-9, AIV-22) returns the ticket number pointed by it"""
        linked_tickets=[]
        try:    
            response = self.session.get(self.baseURL+'/rest/api/%s/issue/%s/remotelink' % (self.version,key))
            if response.status_code == 200:
                # Not all resources will return 200 on success. 
                links = convert_to_ascii(response.json())
                for link in links:
                    url=link['object']['url'].split('/')
                    url=url[url.__len__()-1]
                    linked_tickets.append(str(url).upper())
            return linked_tickets
        except Exception:
            print "Error fetching issue: "+key
            print str(traceback.format_exc())
            return []
                
    def find_issues(self,jqlQuery):
        """Search for issues matching the provided jqlQuery. It returns a dictionary which key the ticket
        number and value =[summary, status and assignee,issue_type]"""        
        try:
            # create payload with a dictionary (minimum fields, since not needed)
            data = { "jql": jqlQuery , "startAt": 0, "maxResults": 300, "fields": ["summary", "status", "assignee","issuetype"] }
            # do a POST since this is most efficient
            response = self.session.post(self.baseURL+'/rest/api/'+self.version+'/search', json.dumps( data ,encoding ='ascii'), headers = {'Content-Type' : 'application/json'})
        except Exception, ex:
            print "EXCEPTION: %s " % ex
            return [];
        # A successful response have an HTTP 200 status as return (from Doc)
        if response.status_code != 200:
            # in some cases, a correct empty answer is receiving 400, since that's not an error, I'm omitting the print for now 
            # print "ERROR: status %s" % response.status_code
            return [];
        # Convert the text in the reply into a Python dictionary
        jqlReply=convert_to_ascii(response.json(encoding='ascii'))
        issues_list={}
        for issue in jqlReply['issues']:
            summary=issue['fields']['summary']
            assignee=issue['fields']['assignee']['name']
            status=issue['fields']['status']['name']
            issue_type=issue['fields']['issuetype']['name']
            issues_list[issue['key']]=[summary,status,assignee,issue_type]
        return issues_list
        
        
        

