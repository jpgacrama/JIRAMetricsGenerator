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

class JIRAService(object):
    username = None
    api_token = None
    jiraService = None
    
    def __init__(self):
        pass

    def logInToJIRA(self):
        username = input("Please enter your username: ")
        api_token = input("Please enter your api-token: ")
        self.jiraService = JIRA(URL, basic_auth=(username, api_token))

    def queryJIRA(self):
        # NOTE:
        # You need to create two JIRA queries: one where you can access the worklog
        # And another to access the Issue types... WHY? 
        allIssuesFromAustin = self.jiraService.search_issues(
            f'assignee in ({members["Austin"]}) AND project = {PROJECT}')

        allWorklogsFromAustin = self.jiraService.search_issues(
            f'assignee in ({members["Austin"]}) AND project = {PROJECT}', fields="worklog")

        return allIssuesFromAustin, allWorklogsFromAustin

class GenerateMetrics(object):
    allIssues = None
    allWorklogs = None
    
    def __init__(self, allIssues, allWorklogs):
        self.allIssues = allIssues
        self.allWorklogs = allWorklogs

    def getDesiredMonth(self):
        month = input("Enter the desired Month in number form: ")
        return int(month)

    def getAllInProgressWorklogs(self):
        desiredMonth = self.getDesiredMonth()

        for value in self.allWorklogs:
            # print(dir(value.fields.issuetype))
            
            log_entry_count = len(value.fields.worklog.worklogs)

            for i in range(log_entry_count):
                dateOfLog = value.fields.worklog.worklogs[i].updated
                dateOfLog = dateOfLog.split(" ")
                dateOfLog[-1] = dateOfLog[-1][:10]
                dateOfLog = " ".join(dateOfLog)
                extractedDateTime = datetime.strptime(dateOfLog, "%Y-%m-%d")

                if extractedDateTime.month == desiredMonth:
                    print(dir(value.fields))
                    print ( value.key, 
                            value.fields.issuetype.description,
                            value.fields.worklog.worklogs[i].timeSpent,
                            value.fields.worklog.worklogs[i].updateAuthor,
                            value.fields.worklog.worklogs[i].updated)

def main():
    jiraService = JIRAService()
    jiraService.logInToJIRA()
    allIssuesFromAustin, allWorklogsFromAustin = jiraService.queryJIRA()

    metrics = GenerateMetrics(jiraLogInResult)
    metrics.getAllInProgressWorklogs(jiraLogInResult)

if __name__ == "__main__":
    main()