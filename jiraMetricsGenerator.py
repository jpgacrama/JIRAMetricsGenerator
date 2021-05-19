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

# Generic plotter function
def plotData(dictionaryWorklog, person):
    if dictionaryWorklog == None or len(dictionaryWorklog) == 0 or person == None:
        print("You cannot plot data without any entries")
        exit(1)
    else:
        numerOfItems = len(dictionaryWorklog)
        pyplot.axis("equal")
        pyplot.pie( [float(v) for v in dictionaryWorklog.values()], 
                    labels = [str(k) for k in dictionaryWorklog],
                    autopct = '%.2f')
        pyplot.title(f"Hours distributon for {person} shown in percent")
        pyplot.show()

# Another helper function to get all worklogs in a specific SW
def getTimeSpentPerJiraItem(desiredMonth, software):
    previousKey = None
    totalTimeSpent = 0
    timeHelper = TimeHelper()
    dictionaryWorklog = {}

    for value in software:
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
                    totalTimeSpent = timeHelper.convertToHours(totalTimeSpent)
                    dictionaryWorklog[previousKey] = totalTimeSpent
                else:
                    totalTimeSpent += value.fields.worklog.worklogs[i].timeSpentSeconds
                    totalTimeSpent = timeHelper.convertToHours(totalTimeSpent)
                    dictionaryWorklog[value.key] = totalTimeSpent

    return dictionaryWorklog             

# Helper function to get Work Logs per SW
def getWorkLogsForEachSW(month, software):
    previousKey = None
    dictionaryWorklog = {}
    timeHelper = TimeHelper()
    
    if (software != None):
        for sw in software:
            dictionaryWorklog[sw] = {}
            for value in software[sw]:
                numberOfJiraTicketsForEachSW = len(value.fields.worklog.worklogs)
                    
                for i in range(numberOfJiraTicketsForEachSW):
                    extractedDateTime = timeHelper.trimDate(value, i)
                    if extractedDateTime.month == month:
                        if previousKey != value.key:
                            previousKey = value.key
                            totalTimeSpent = value.fields.worklog.worklogs[i].timeSpentSeconds
                            totalTimeSpent = timeHelper.convertToHours(totalTimeSpent)
                            dictionaryWorklog[sw][previousKey] = totalTimeSpent
                        else:
                            totalTimeSpent += value.fields.worklog.worklogs[i].timeSpentSeconds
                            totalTimeSpent = timeHelper.convertToHours(totalTimeSpent)
                            dictionaryWorklog[sw][value.key] = totalTimeSpent
                
            dictionaryWorklog[sw] = sum(dictionaryWorklog[sw].values())

        return dictionaryWorklog

    else:
        print("TimeSpentPerSoftware.extractItemsPerSW() should be run first.")
        exit()

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

# This Class is responsible for logging in to JIRA and performing Queries
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

# This class is responsible for querying each of the
# PROJECT items belonging to the various SW
class TimeSpentPerSoftware(object):
    software = {}
    month = None

    def __init__(self) -> None:
        super().__init__()

    def extractItemsPerSW(self, memberToQuery, jIRAService):
        for sw in SOFTWARE:
            self.software[sw] = jIRAService.queryJIRA(memberToQuery, sw)

    def getDesiredMonth(self):
        self.month = int(input("Enter the desired Month in number form: "))
        return self.month

    def getTimeSpentForEachSW(self):
        return getWorkLogsForEachSW(self.getDesiredMonth(), self.software)
        
class TimeSpentPerWorkItemInASpecificSW(object):
    software = {}
    month = None
    
    def __init__(self) -> None:
        super().__init__()

    def extractJiraTickets(self, memberToQuery, softwareName, jIRAService):
        self.software = jIRAService.queryJIRA(memberToQuery, softwareName)

    def getDesiredMonth(self):
        self.month = int(input("Enter the desired Month in number form: "))
        return self.month

    def getTimeSpentForAllItemsInASpecificSW(self):
        return getTimeSpentPerJiraItem(self.getDesiredMonth(), self.software)

def main():
    jiraService = JIRAService()
    jiraService.logInToJIRA()
    
    # AUSTIN
    timeSpentPerWorkItemInASpecificSW = TimeSpentPerWorkItemInASpecificSW()
    timeSpentPerWorkItemInASpecificSW.extractJiraTickets(
        "Austin", "Macrovue", jiraService)
    worklog = timeSpentPerWorkItemInASpecificSW.getTimeSpentForAllItemsInASpecificSW()
    plotData(worklog, "Austin")

    # JERRED
    timeSpentPerSoftware = TimeSpentPerSoftware()
    timeSpentPerSoftware.extractItemsPerSW("Jerred", jiraService)
    worklog = timeSpentPerSoftware.getTimeSpentForEachSW()
    plotData(worklog, "Jerred")
    
if __name__ == "__main__":
    main()