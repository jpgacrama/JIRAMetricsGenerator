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

class TimeHelper(object):
    def trimDate(self, jiraValue, index):
        dateOfLog = jiraValue.fields.worklog.worklogs[index].updated
        dateOfLog = dateOfLog.split(" ")
        dateOfLog[-1] = dateOfLog[-1][:10]
        dateOfLog = " ".join(dateOfLog)
        extractedDateTime = datetime.strptime(dateOfLog, "%Y-%m-%d")
        return extractedDateTime

    def convertToHours(self, timeInSeconds):
        timeInHours = round(timeInSeconds / (60*60), 2)
        return timeInHours

# This class is responsible for querying each of the
# OMNI items belonging to the various SW
class TimeSpentPerSoftware(object):
    software = {}
    month = None
    timeHelper = None

    def __init__(self) -> None:
        super().__init__()
        self.timeHelper = TimeHelper()

    def extractItemsPerSW(self, memberToQuery, jIRAService):
        for sw in SOFTWARE:
            self.software[sw] = jIRAService.queryJIRA(memberToQuery, sw)

    def setDesiredMonth(self):
        self.month = int(input("Enter the desired Month in number form: "))

    def calculateTimeSpentForEachSW(self):
        previousKey = None
        dictionaryWorklog = {}

        self.setDesiredMonth()
        
        if (self.software != None):
            for sw in self.software:
                dictionaryWorklog[sw] = {}
                for value in self.software[sw]:
                    numberOfJiraTicketsForEachSW = len(value.fields.worklog.worklogs)
                    
                    for i in range(numberOfJiraTicketsForEachSW):
                        extractedDateTime = self.timeHelper.trimDate(value, i)
                        if extractedDateTime.month == self.month:
                            if previousKey != value.key:
                                previousKey = value.key
                                totalTimeSpent = value.fields.worklog.worklogs[i].timeSpentSeconds
                                totalTimeSpent = self.timeHelper.convertToHours(totalTimeSpent)
                                dictionaryWorklog[sw][previousKey] = totalTimeSpent
                            else:
                                totalTimeSpent += value.fields.worklog.worklogs[i].timeSpentSeconds
                                totalTimeSpent = self.timeHelper.convertToHours(totalTimeSpent)
                                dictionaryWorklog[sw][value.key] = totalTimeSpent

            return dictionaryWorklog

        else:
            print("TimeSpentPerSoftware.extractItemsPerSW() should be run first.")
            exit()

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

    def getTimeSpentPerJiraItem(self, allWorklogs):
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
    # allWorklogsFromAustin = jiraService.queryJIRA("Austin", "Macrovue")
    # timeConverter = TimeConverter()

    # worklogs = {}
    # issues = {}
    # metrics = GenerateMetrics(allWorklogsFromAustin, timeConverter)
    
    # worklogs = metrics.getTimeSpentPerJiraItem(allWorklogsFromAustin)
    # metrics.plotData(worklogs, "Austin")

    # JERRED
    timeSpentPerSoftware = TimeSpentPerSoftware()
    timeSpentPerSoftware.extractItemsPerSW("Jerred", jiraService)
    timeSpentPerSoftware.calculateTimeSpentForEachSW()
    
    # allWorklogsFromJerred = jiraService.queryJIRA("Jerred")
    # timeConverter = TimeConverter()

    # worklogs = {}
    # issues = {}
    # metrics = GenerateMetrics(allWorklogsFromJerred, timeConverter)
    
    # worklogs = metrics.getTimeSpentPerJiraItem(allWorklogsFromJerred)
    # metrics.plotData(worklogs, "Jerred")

if __name__ == "__main__":
    main()