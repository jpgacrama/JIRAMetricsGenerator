#!/usr/bin/env python3

import os
from jira import JIRA
from datetime import datetime
import matplotlib.pyplot as pyplot
import pandas as pd

URL = 'https://macrovue.atlassian.net'
PROJECT = 'OMNI'
MEMBERS = {
    # 'Arman'     : '6057df8914a23b0069a65dc8',
    # 'Austin'    : '5fbb3d037cc1030069500950',
    # 'Duane'     : '5efbf73454020e0ba82ac7a0',
    # 'Eddzonne'  : '5f85328a53aaa400760d4944',
    # 'Florante'  : '5fa0b7ad22f39900769a8242',
    # 'Jansseen'  : '5f3b1fd49aa9650046aeffb6',
    'Jaypea'    : '6073ef399361560068ad4b83',
    # 'Jerred'    : '5ed4c8d844cc830c23027b31',
    # 'Juliet'    : '5fa89a11ecdae600684d1dc8',
    # 'Marwin'    : '600e2429cd564b0068e7cca7',
    # 'Mary'      : '6099e1699b362f006957e1ad',
    # 'Maye'      : '6099d80c3fae6f006821f3f5',
    # 'Nicko'     : '5f3b1fd4ea5e2f0039697b3d',
    # 'Ranniel'   : '604fe79ce394c300699ce0ed',
    'Ronald'    : '5fb1f35baa1d30006fa6a618'
}

SOFTWARE = ['Infrastructure',
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
        pyplot.pie( [float(v) for v in dictionaryWorklog.values() if v != 0],
                    labels = [str(k) for k,v in dictionaryWorklog.items() if v != 0],
                    autopct = lambda p: '{:.2f}%'.format(round(p, 2)) if p > 0 else '')
        pyplot.title(f"Hours distributon for person shown in percent")
        pyplot.tight_layout()
        pyplot.show()

def computeTotalTimeSpent(numberOfJiraTicketsForEachSW, jiraValue, dictionaryWorklog, sw, month):
    timeHelper = TimeHelper()
    previousKey = None
    totalTimeSpent = 0
    newTimeSpent = 0

    for i in range(numberOfJiraTicketsForEachSW):
        extractedDateTime = timeHelper.trimDate(jiraValue, i)
        if extractedDateTime.month == month:
            if previousKey != jiraValue.key:
                totalTimeSpent = 0                
                previousKey = jiraValue.key
                totalTimeSpent = jiraValue.fields.worklog.worklogs[i].timeSpentSeconds
                totalTimeSpent = timeHelper.convertToHours(totalTimeSpent)
                dictionaryWorklog[sw][previousKey] = totalTimeSpent
            else:
                newTimeSpent = 0
                newTimeSpent = jiraValue.fields.worklog.worklogs[i].timeSpentSeconds
                newTimeSpent = timeHelper.convertToHours(newTimeSpent)
                totalTimeSpent += newTimeSpent
                dictionaryWorklog[sw][previousKey] = totalTimeSpent

    return dictionaryWorklog

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

# Helper function to get Work Logs per SW
def getWorkLogsForEachSW(month, software):
    dictionaryWorklog = {}

    if (software != None):
        for sw in software:
            dictionaryWorklog[sw] = {}
            for value in software[sw]:
                numberOfJiraTicketsForEachSW = len(value.fields.worklog.worklogs)
                dictionaryWorklog = computeTotalTimeSpent(
                    numberOfJiraTicketsForEachSW, value, dictionaryWorklog, sw, month)
            dictionaryWorklog[sw] = round(sum(dictionaryWorklog[sw].values()), 2)

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
            f'assignee in ({MEMBERS[memberToQuery]}) AND project = {PROJECT} AND "Software[Dropdown]" = \"{swToQuery}\"',
                fields="worklog")

        # Returns a list of Worklogs
        return allWorklogs

# This class is responsible for querying each of the
# PROJECT items belonging to the various SW
class TimeSpentPerSoftware(object):
    software = {}

    def __init__(self) -> None:
        super().__init__()

    def extractItemsPerSW(self, memberToQuery, jIRAService):
        for sw in SOFTWARE:
            self.software[sw] = jIRAService.queryJIRA(memberToQuery, sw)

    def getTimeSpentForEachSW(self):
        return getWorkLogsForEachSW(getDesiredMonth(), self.software)

class TimeSpentPerWorkItemInASpecificSW(object):
    software = {}

    def __init__(self) -> None:
        super().__init__()

    def extractJiraTickets(self, memberToQuery, softwareName, jIRAService):
        self.software = jIRAService.queryJIRA(memberToQuery, softwareName)

    def getTimeSpentForAllItemsInASpecificSW(self):
        return getTimeSpentPerJiraItem(getDesiredMonth(), self.software)

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
            df.loc['Column_Total']= df.sum(numeric_only=True, axis=0)
            df.loc[:,'Row_Total'] = df.sum(numeric_only=True, axis=1)
            self.result[1:] = df.values.tolist()

    def generateMatrix(self):
        jiraService = JIRAService()
        jiraService.logInToJIRA()
        timeSpentPerSoftware = TimeSpentPerSoftware()
        numOfPersons = 0

        for person in MEMBERS:
            timeSpentPerSoftware.extractItemsPerSW(str(person), jiraService)
            self.worklog[str(person)] = timeSpentPerSoftware.getTimeSpentForEachSW()
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

        self.result = [[index for index, value in self.worklog.items()]] + list(map(list, zip(*tempResult)))

    # Plots the number of hours spent per person
    def plotMatrix(self):
        figure, axis = pyplot.subplots(1,1)
        data = [i[1:] for i in self.result[1:]]
        column_labels = self.result[0]
        row_labels = [i[0] for i in self.result[1:]]
        axis.axis('tight')
        axis.axis('off')
        table = axis.table(cellText = data, colLabels = column_labels, rowLabels = row_labels, loc="center")
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

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    matrixOfWorklogsPerSW = MatrixOfWorklogsPerSW()
    matrixOfWorklogsPerSW.generateMatrix()
    # matrixOfWorklogsPerSW.plotMatrix()
    matrixOfWorklogsPerSW.writeToCSVFile()

if __name__ == "__main__":
    main()