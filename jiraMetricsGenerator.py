#!/usr/bin/env python3

import os
import jira
os.system('cls' if os.name == 'nt' else 'clear')

from jira import JIRA
from datetime import datetime
import matplotlib.pyplot as pyplot

URL = 'https://macrovue.atlassian.net'
PROJECT = 'OMNI'
MEMBERS = {
    'Austin': '5fbb3d037cc1030069500950',
    'Jerred': '5ed4c8d844cc830c23027b31'
}

SOFTWARE = ['Macrovue',
            'HALO']

# This class is responsible for querying each of the
# OMNI items belonging to the various SW
class TimeSpentPerSoftware(object):
    software = {}

    def extractItemsPerSW(self, memberToQuery, jIRAService):
        for sw in SOFTWARE:
            self.software[sw] = jIRAService.queryJIRA(memberToQuery, sw)

        print(self.software['HALO'])

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

    def queryJIRA(self, memberToQuery, swToQuery):
        allWorklogs = self.jiraService.search_issues(
            f'assignee in ({MEMBERS[memberToQuery]}) AND project = {PROJECT} AND Software = {swToQuery}',
                fields="worklog")

        # Returns a list of Worklogs
        return allWorklogs

class GenerateMetrics(object):
    allWorklogs = None
    TimeConverter = None
    
    def __init__(self, allWorklogs, timeConverter):
        self.allWorklogs = allWorklogs
        self.timeConverter = timeConverter

    def getDesiredMonth(self):
        month = input("Enter the desired Month in number form: ")
        return int(month)


    def getAllInProgressWorklogs(self, allWorklogs):
        desiredMonth = self.getDesiredMonth()
        previousKey = None
        totalTimeSpent = 0
        dictionaryWorklog = {}

        for value in self.allWorklogs:
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

        return dictionaryWorklog

    # Function to plot the hours spent for each JIRA ID
    # TODO: I need to plot this against SW, but I need to extract its custom ID
    def plotData(self, dictionaryWorklog, person):
        numerOfItems = len(dictionaryWorklog)
        pyplot.axis("equal")
        pyplot.pie( [float(v) for v in dictionaryWorklog.values()], 
                    labels = [str(k) for k in dictionaryWorklog],
                    autopct = '%.2f')
        pyplot.title(f"Hours distributon for {person} shown in percent")
        pyplot.show()

def main():
    jiraService = JIRAService()
    jiraService.logInToJIRA()
    
    # AUSTIN
    # allWorklogsFromAustin = jiraService.queryJIRA("Austin")

    # timeConverter = TimeConverter()

    # worklogs = {}
    # issues = {}
    # metrics = GenerateMetrics(allWorklogsFromAustin, timeConverter)
    
    # worklogs = metrics.getAllInProgressWorklogs(allWorklogsFromAustin)
    # metrics.plotData(worklogs, "Austin")

    # JERRED
    timeSpentPerSoftware = TimeSpentPerSoftware()
    timeSpentPerSoftware.extractItemsPerSW("Jerred", jiraService)
    
    # allWorklogsFromJerred = jiraService.queryJIRA("Jerred")
    # timeConverter = TimeConverter()

    # worklogs = {}
    # issues = {}
    # metrics = GenerateMetrics(allWorklogsFromJerred, timeConverter)
    
    # worklogs = metrics.getAllInProgressWorklogs(allWorklogsFromJerred)
    # metrics.plotData(worklogs, "Jerred")

if __name__ == "__main__":
    main()