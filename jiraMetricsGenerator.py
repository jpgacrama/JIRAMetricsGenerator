#!/usr/bin/env python3

import os
import jira
os.system('cls' if os.name == 'nt' else 'clear')

from jira import JIRA
from datetime import datetime

URL = 'https://macrovue.atlassian.net'
PROJECT = 'OMNI'
members = {
    'Austin': '5fbb3d037cc1030069500950'
}

class JIRALoginAndQuery():
    username = None
    api_token = None
    
    def __init__(self):
        pass

    def logInToJIRA(self):
        username = input("Please enter your username: ")
        api_token = input("Please enter your api-token: ")
        jiraLogInResult = JIRA(URL, basic_auth=(username, api_token))
        return jiraLogInResult

    def queryJIRA(self):
        # NOTE:
        # You need to create two JIRA queries: one where you can access the worklog
        # And another to access the Issue types... WHY? 
        allIssuesFromAustin = self.jira.search_issues(
            f'assignee in ({members["Austin"]}) AND project = {PROJECT}')

        allWorklogsFromAustin = self.jira.search_issues(
            f'assignee in ({members["Austin"]}) AND project = {PROJECT}', fields="worklog")

        return allIssuesFromAustin, allWorklogsFromAustin

class GenerateMetrics(object):
    jira = None
    
    def __init__(self, jira):
        self.jira = jira

    def getDesiredMonth(self):
        month = input("Enter the desired Month in number form: ")
        return int(month)

    def getAllInProgressTasksFromAustin(self, jira):
        desiredMonth = self.getDesiredMonth()


        
        for value in allIssuesFromAustin:
            print(dir(value.fields.issuetype))
            
            # log_entry_count = len(value.fields.worklog.worklogs)

            # for i in range(log_entry_count):
            #     dateOfLog = value.fields.worklog.worklogs[i].updated
            #     dateOfLog = dateOfLog.split(" ")
            #     dateOfLog[-1] = dateOfLog[-1][:10]
            #     dateOfLog = " ".join(dateOfLog)
            #     extractedDateTime = datetime.strptime(dateOfLog, "%Y-%m-%d")

            #     if extractedDateTime.month == desiredMonth:
            #         print(dir(value.fields))
            #         print ( value.key, 
            #                 value.fields.issuetype.description,
            #                 value.fields.worklog.worklogs[i].timeSpent,
            #                 value.fields.worklog.worklogs[i].updateAuthor,
            #                 value.fields.worklog.worklogs[i].updated)

def main():
    jiraQuery = JIRALoginAndQuery()
    jiraLogInResult = jiraQuery.logInToJIRA()
    
    metrics = GenerateMetrics(jiraLogInResult)
    metrics.getAllInProgressTasksFromAustin(jiraLogInResult)

if __name__ == "__main__":
    main()