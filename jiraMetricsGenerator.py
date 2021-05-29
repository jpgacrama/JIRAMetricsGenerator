#!/usr/bin/env python3

import os
from jira import JIRA
from datetime import datetime
import matplotlib.pyplot as pyplot
import pandas as pd

URL = 'https://macrovue.atlassian.net'
PROJECT = 'OMNI'
MEMBERS = {
    'Arman'     : '6057df8914a23b0069a65dc8',
    'Austin'    : '5fbb3d037cc1030069500950',
    'Duane'     : '5efbf73454020e0ba82ac7a0',
    'Eddzonne'  : '5f85328a53aaa400760d4944',
    'Florante'  : '5fa0b7ad22f39900769a8242',
    'Jansseen'  : '5f3b1fd49aa9650046aeffb6',
    'Jaypea'    : '6073ef399361560068ad4b83',
    'Jerred'    : '5ed4c8d844cc830c23027b31',
    'Juliet'    : '5fa89a11ecdae600684d1dc8',
    'Marwin'    : '600e2429cd564b0068e7cca7',
    'Mary'      : '6099e1699b362f006957e1ad',
    'Maye'      : '6099d80c3fae6f006821f3f5',
    'Nicko'     : '5f3b1fd4ea5e2f0039697b3d',
    'Ranniel'   : '604fe79ce394c300699ce0ed',
    'Ronald'    : '5fb1f35baa1d30006fa6a618'
}

SOFTWARE = [
    'Infrastructure',
    'AAIG CRM',
    'ASR Reports',
    'Wordpress CMS Websites',
    'Hubspot CMS Websites',
    'Macrovue',
    'Macrovue Marketing',
    'HALO',
    'HALO Mobile',
    'HALO Marketing',
    'Notification',
    'Ascot',
    'CMA',
    'R:Ed']

DESIRED_MONTH = None

# Helper function to get the desired month
def getDesiredMonth():
    global DESIRED_MONTH
    if DESIRED_MONTH == None:
        DESIRED_MONTH = int(input("Enter the desired Month in number form: "))

    return DESIRED_MONTH

# Generic plotter function
def plotData(dictionaryWorklog, person):
    if dictionaryWorklog == None or len(dictionaryWorklog) == 0 or person == None:
        print("You cannot plot data without any entries")
        exit(1)
    else:
        numerOfItems = len(dictionaryWorklog)
        pyplot.axis("equal")
        pyplot.pie([float(v) for v in dictionaryWorklog.values() if v != 0],
                   labels=[str(k)
                           for k, v in dictionaryWorklog.items() if v != 0],
                   autopct=lambda p: '{:.2f}%'.format(round(p, 2)) if p > 0 else '')
        pyplot.title(f"Hours distributon for person shown in percent")
        pyplot.tight_layout()
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
                    newTimeSpent = 0
                    newTimeSpent = value.fields.worklog.worklogs[i].timeSpentSeconds
                    newTimeSpent = timeHelper.convertToHours(newTimeSpent)
                    totalTimeSpent += newTimeSpent

                    dictionaryWorklog[value.key] = totalTimeSpent

    return dictionaryWorklog

class TimeHelper(object):
    def trimDate(self, jiraValue):
        dateOfLog = jiraValue.updated
        dateOfLog = dateOfLog.split(" ")
        dateOfLog[-1] = dateOfLog[-1][:10]
        dateOfLog = " ".join(dateOfLog)
        extractedDateTime = datetime.strptime(dateOfLog, "%Y-%m-%d")
        return extractedDateTime

    def convertToHours(self, timeInSeconds):
        timeInHours = round(timeInSeconds / (60*60), 2)
        return timeInHours

# Helper function to get Work Logs per SW
class WorkLogsForEachSW(object):
    dictionaryWorklog = {}
    timeHelper = TimeHelper()
    issueId = None
    totalTimeSpent = 0
    newTimeSpent = 0

    def __computeTotalTimeSpent__(self, value, sw, month):
        self.issueId = None
        self.totalTimeSpent = 0
        self.newTimeSpent = 0

        # nLogs means first log, second log, etc.
        for nLogs in value:
            extractedDateTime = self.timeHelper.trimDate(nLogs)
            if extractedDateTime != None:
                if extractedDateTime.month == month:
                    if self.issueId != nLogs.issueId:
                        self.totalTimeSpent = 0
                        self.issueId = nLogs.issueId
                        self.totalTimeSpent = nLogs.timeSpentSeconds
                        self.totalTimeSpent = self.timeHelper.convertToHours(self.totalTimeSpent)
                        self.dictionaryWorklog[sw][self.issueId] = self.totalTimeSpent
                    else:
                        newTimeSpent = 0
                        newTimeSpent = nLogs.timeSpentSeconds
                        newTimeSpent = self.timeHelper.convertToHours(newTimeSpent)
                        self.totalTimeSpent += newTimeSpent
                        self.dictionaryWorklog[sw][self.issueId] = self.totalTimeSpent

    def getWorkLogsForEachSW(self, month, software):
        self.dictionaryWorklog = {}
        if (software != None):
            for sw in software:
                self.dictionaryWorklog[sw] = {}
                for value in software[sw].values():
                    self.__computeTotalTimeSpent__(value, sw, month)
                self.dictionaryWorklog[sw] = round(sum(self.dictionaryWorklog[sw].values()), 2)
            return self.dictionaryWorklog

        else:
            print("TimeSpentPerSoftware.extractItemsPerSW() should be run first.")
            exit()

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

    def queryJIRAPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f'assignee in ({MEMBERS[person]}) AND project = {PROJECT}',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

    def queryJIRA(self, memberToQuery, swToQuery):
        allIssues = self.jiraService.search_issues(
            f'assignee in ({MEMBERS[memberToQuery]}) AND project = {PROJECT} AND "Software[Dropdown]" = \"{swToQuery}\"',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

# This class is responsible for querying each of the
# PROJECT items belonging to the various SW
class TimeSpentPerSoftware(object):
    software = {}
    worklogsForEachSW = WorkLogsForEachSW()

    def __init__(self) -> None:
        super().__init__()

    def extractItemsPerSW(self, memberToQuery, jIRAService):
        self.software = {}
        for sw in SOFTWARE:
            self.software[sw] = jIRAService.queryJIRA(memberToQuery, sw)

    def getTimeSpentForEachSW(self):
        return self.worklogsForEachSW.getWorkLogsForEachSW(getDesiredMonth(), self.software)

# This will be the "Caller" class
class MatrixOfWorklogsPerSW(object):
    result = []
    worklog = {}

    # Function to get the total hours spent for every SW
    def __getTotal__(self):
        if len(self.result) == 0:
            print("You need to call MatrixOfWorklogsPerSW.generateMatrix() first")
            exit(1)
        else:
            df = pd.DataFrame(self.result[1:])
            df.loc['Column_Total'] = df.sum(numeric_only=True, axis=0)
            df.loc[:, 'Row_Total'] = df.sum(numeric_only=True, axis=1)
            self.result[1:] = df.values.tolist()

    def generateMatrix(self):
        jiraService = JIRAService()
        jiraService.logInToJIRA()
        timeSpentPerSoftware = TimeSpentPerSoftware()
        numOfPersons = 0

        for person in MEMBERS:
            timeSpentPerSoftware.extractItemsPerSW(person, jiraService)
            self.worklog[person] = timeSpentPerSoftware.getTimeSpentForEachSW()
            numOfPersons += 1
            progress = round(100 * (numOfPersons / len(MEMBERS)), 2)
            print(f"Getting data for: {person:<10} Progress in percent: {progress:^5}")

        tempData = list(self.worklog.values())
        subset = set()
        for element in tempData:
            for index in element:
                subset.add(index)
        tempResult = []
        tempResult.append(subset)
        for key, value in self.worklog.items():
            tempData2 = []
            for index in subset:
                tempData2.append(value.get(index, 0))
            tempResult.append(tempData2)

        self.result = [[index for index, value in self.worklog.items()]] + \
            list(map(list, zip(*tempResult)))

    # Plots the number of hours spent per person
    def plotMatrix(self):
        figure, axis = pyplot.subplots(1, 1)
        data = [i[1:] for i in self.result[1:]]
        column_labels = self.result[0]
        row_labels = [i[0] for i in self.result[1:]]
        axis.axis('tight')
        axis.axis('off')
        table = axis.table(cellText=data, colLabels=column_labels,
                           rowLabels=row_labels, loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        pyplot.show()

    def writeToCSVFile(self):
        if len(self.result) != 0:
            self.__getTotal__()
            fileName = input("Please enter the fileame you wish to write the CSV values to: ")
            self.result[0].insert(0, 'SW Names')
            df = pd.DataFrame(self.result)
            df.to_csv(fileName, index=False, header=False)
            print(f"Writing to {fileName} done.")
        else:
            print("You need to call MatrixOfWorklogsPerSW.generateMatrix() first.")
            exit(1)

class TimeSpentPerPerson(object):
    worklogPerPerson = {}
    jiraService = None
    issueId = None
    personKey = None
    matrix = None
    timeHelper = TimeHelper()

    def __init__(self, jiraService) -> None:
        super().__init__()
        self.jIRAService = jiraService

    def __extractItemsPerPerson__(self):
        itemsPerPerson = {}
        numOfPersons = 0
        for person in MEMBERS:
            numOfPersons += 1
            progress = round(100 * (numOfPersons / len(MEMBERS)), 2)
            print(f"Getting data for: {person:<10} Progress in percent: {progress:^5}")
            itemsPerPerson[person] = self.jIRAService.queryJIRAPerPerson(person)

        return itemsPerPerson

    def __extractTime__(self, logsPerValue, month, person):
        if self.personKey != person:
            self.worklogPerPerson[person] = 0
            self.personKey = person

        extractedDateTime = self.timeHelper.trimDate(logsPerValue)
        if extractedDateTime != None:
            if extractedDateTime.month == month:
                self.issueId = logsPerValue.issueId
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerPerson[person] += timeSpent

    def extractTimeSpentPerPerson(self):
        allWorklogs = self.__extractItemsPerPerson__()
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:
                for worklogPerJIRAId in allWorklogs[person][jiraID]:
                    self.__extractTime__(worklogPerJIRAId, getDesiredMonth(), person)

    def genrateCSVFile(self):
        df = pd.DataFrame(self.worklogPerPerson, index=[0])
        fileName = input("Please enter the fileame you wish to write the CSV values to: ")
        df.to_csv(fileName, index=False, header=MEMBERS.keys())


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    # matrixOfWorklogsPerSW = MatrixOfWorklogsPerSW()
    # matrixOfWorklogsPerSW.generateMatrix()
    # # matrixOfWorklogsPerSW.plotMatrix()
    # matrixOfWorklogsPerSW.writeToCSVFile()

    jiraService = JIRAService()
    jiraService.logInToJIRA()

    timeSpentPerPerson = TimeSpentPerPerson(jiraService)
    timeSpentPerPerson.extractTimeSpentPerPerson()
    timeSpentPerPerson.genrateCSVFile()

if __name__ == "__main__":
    main()
