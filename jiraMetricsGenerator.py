#!/usr/bin/env python3

import os
import jira
os.system('cls' if os.name == 'nt' else 'clear')

from jira import JIRA
from datetime import datetime
import numpy as np

URL = 'https://macrovue.atlassian.net'
PROJECT = 'OMNI'
members = {
    'Austin': '5fbb3d037cc1030069500950'
}

class TimeConverter(object):
    # Converts the time to hours given the number in seconds
    def convertToHours(self, timeInSeconds):
        timeInHours = round(timeInSeconds / (60*60), 2)
        return timeInHours

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
    TimeConverter = None
    
    def __init__(self, allIssues, allWorklogs, timeConverter):
        self.allIssues = allIssues
        self.allWorklogs = allWorklogs
        self.timeConverter = timeConverter

    def getDesiredMonth(self):
        month = input("Enter the desired Month in number form: ")
        return int(month)

    # Issues contain information about Issue Types
    # It may contain the SW and Component fields. But I still need to investigate this
    def getAllInProgressIssues(self, allIssues):
        pass

    # Worklogs contains all time spent information.
    # I want to transform this into a matrix for now, so I can plot it
    def getAllInProgressWorklogs(self, allWorklogs):
        desiredMonth = self.getDesiredMonth()
        previousKey = None
        totalTimeSpent = 0
        dictionaryWorklog = {}

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
                    if previousKey != value.key:
                        previousKey = value.key

                        totalTimeSpent = value.fields.worklog.worklogs[i].timeSpentSeconds
                        totalTimeSpent = self.timeConverter.convertToHours(totalTimeSpent)
                        dictionaryWorklog[previousKey] = totalTimeSpent
                    else:
                        totalTimeSpent += value.fields.worklog.worklogs[i].timeSpentSeconds
                        totalTimeSpent = self.timeConverter.convertToHours(totalTimeSpent)
                        dictionaryWorklog[value.key] = totalTimeSpent

                    # Debug print to show the non-cumulative values of timeSpent
                    # print ( value.key, 
                    #         value.fields.worklog.worklogs[i].timeSpent)

                    # Some items you may be interested in the future:
                    # - value.fields.issuetype.description
                    # - value.fields.worklog.worklogs[i].updateAuthor
                    # - value.fields.worklog.worklogs[i].updated

        print(dictionaryWorklog)

    def transformDictionaryToMatrix(self):
        pass

    # Function to plot the hours spent for each JIRA ID
    # TODO: I need to plot this against SW, but I need to extract its custom ID
    def plotData(self):
        pass

def main():
    jiraService = JIRAService()
    jiraService.logInToJIRA()
    allIssuesFromAustin, allWorklogsFromAustin = jiraService.queryJIRA()

    timeConverter = TimeConverter()

    metrics = GenerateMetrics(allIssuesFromAustin, allWorklogsFromAustin, timeConverter)
    metrics.getAllInProgressWorklogs(allWorklogsFromAustin)

if __name__ == "__main__":
    main()