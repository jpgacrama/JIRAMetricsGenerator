#!/usr/bin/env python3

from logging import NOTSET
import os
from jira import JIRA
from datetime import datetime
import pandas as pd
import csv
import threading

URL = 'https://macrovue.atlassian.net'
PROJECT = 'OMNI'

MEMBERS = {
    # 'Arman'     : '6057df8914a23b0069a65dc8',
    # 'Austin'    : '5fbb3d037cc1030069500950',
    # 'Daniel'    : '61076053fc68c10069c80eba'
    # 'Duane'     : '5efbf73454020e0ba82ac7a0',
    # 'Eddzonne'  : '5f85328a53aaa400760d4944',
    # 'Florante'  : '5fa0b7ad22f39900769a8242',
    # 'Harold'    : '60aaff8d5dc18500701239c0',
    'Jansseen'  : '5f3b1fd49aa9650046aeffb6',
    # 'Jaypea'    : '6073ef399361560068ad4b83',
    # 'Jerred'    : '5ed4c8d844cc830c23027b31',
    # 'Juliet'    : '5fa89a11ecdae600684d1dc8',
    # 'Marwin'    : '600e2429cd564b0068e7cca7',
    # 'Mary'      : '6099e1699b362f006957e1ad',
    # 'Maye'      : '6099d80c3fae6f006821f3f5',
    # 'Nicko'     : '5f3b1fd4ea5e2f0039697b3d',
    # 'Ranniel'   : '604fe79ce394c300699ce0ed',
    # 'Ronald'    : '5fb1f35baa1d30006fa6a618'
}

ISSUE_TYPES = ['Project', 'Ad-hoc']

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
DESIRED_YEAR = None
DONE_LIST = "Closed, Done, \"READY FOR PROD RELEASE\""

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Only JIRA Query can filter out DONE Items. 
# You need to MANUALLY EDIT THE START AND END DATES to your desired month

WORKLOG_DATE = "worklogDate >= \"2021-07-01\" AND worklogDate < \"2021-07-31\""
UPDATED_DATE = "updated >= 2021-07-01 AND updated <= 2021-07-31"

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!! WARNING !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Update this for a RANGE of JIRA Items
SPRINT = "(186, 187, 188, 189, 190, 191)"

# Helper function to get the desired month
def getDesiredSprintYearAndMonth():
    global DESIRED_MONTH, DESIRED_YEAR, SPRINT

    if not SPRINT:
        SPRINT in int(input("Enter the Sprint using the value from JIRA Query: "))

    if not DESIRED_YEAR:
        DESIRED_YEAR = int(input("Enter the desired Year: "))
    
    if not DESIRED_MONTH:
        DESIRED_MONTH = int(input("Enter the desired Month in number form: "))
        print("\n")

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

# Helper Class to get Work Logs per SW
class WorkLogsForEachSW(object):
    def __init__(self) -> None:
        super().__init__()
        self.dictionaryWorklog = {}
        self.timeHelper = TimeHelper()
        self.issueId = None
        self.totalTimeSpent = 0
        self.newTimeSpent = 0

    def __computeTotalTimeSpent__(self, value, person, sw):
        self.issueId = None
        self.totalTimeSpent = 0
        self.newTimeSpent = 0

        # nLogs means first log, second log, etc.
        for nLogs in value:
            extractedDateTime = self.timeHelper.trimDate(nLogs)
            if extractedDateTime:
                if extractedDateTime.month == DESIRED_MONTH and extractedDateTime.year == DESIRED_YEAR:
                    if self.issueId != nLogs.issueId:
                        self.totalTimeSpent = 0
                        self.issueId = nLogs.issueId
                        self.totalTimeSpent = nLogs.timeSpentSeconds
                        self.totalTimeSpent = self.timeHelper.convertToHours(self.totalTimeSpent)
                        self.dictionaryWorklog[person][sw][self.issueId] = self.totalTimeSpent
                    else:
                        newTimeSpent = 0
                        newTimeSpent = nLogs.timeSpentSeconds
                        newTimeSpent = self.timeHelper.convertToHours(newTimeSpent)
                        self.totalTimeSpent += newTimeSpent
                        self.dictionaryWorklog[person][sw][self.issueId] = self.totalTimeSpent

    def getWorkLogsForEachSW(self, software, person):
        self.dictionaryWorklog[person] = {}
        if software:
            for sw in software:
                self.dictionaryWorklog[person][sw] = {}
                for value in software[sw].values():
                    self.__computeTotalTimeSpent__(value, person, sw)
                self.dictionaryWorklog[person][sw] = round(sum(self.dictionaryWorklog[person][sw].values()), 2)
            return self.dictionaryWorklog

        else:
            print("TimeSpentPerSoftware.extractItemsPerSW() should be run first.")
            exit()

# This Class is responsible for logging in to JIRA and performing Queries
class JIRAService(object):
    def __init__(self) -> None:
        super().__init__()
        self.__logInToJIRA__()
        self.username = None
        self.api_token = None

    def __logInToJIRA__(self):
        username = input("Please enter your username: ")
        api_token = input("Please enter your api-token: ")
        self.jiraService = JIRA(URL, basic_auth=(username, api_token))

    def queryNumberOfDoneItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f"""
                {UPDATED_DATE}
                AND assignee in ({MEMBERS[person]})
                AND project = {PROJECT}
                AND status in ({DONE_LIST})
             """,
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = {}
            allWorklogs[str(issue)]['description'] = {}
            allWorklogs[str(issue)]['timeSpent'] = {}
            allWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            allWorklogs[str(issue)]['timeSpent'] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

    # WARNING!! 
    # I did not use any SPRINT values here
    def queryRawItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f"""
                {WORKLOG_DATE}
                AND assignee in ({MEMBERS[person]})
                AND project = {PROJECT}
             """,
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = {}
            allWorklogs[str(issue)]['description'] = {}
            allWorklogs[str(issue)]['Software'] = {}
            allWorklogs[str(issue)]['Component'] = {}
            allWorklogs[str(issue)]['Story Point'] = {}
            allWorklogs[str(issue)]['Date Started'] = {}
            allWorklogs[str(issue)]['Date Finished'] = {}
            allWorklogs[str(issue)]['timeSpent'] = {}
            
            allWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            allWorklogs[str(issue)]['timeSpent'] = self.jiraService.worklogs(issue)

            if self.jiraService.issue(str(issue)).raw['fields']['customfield_11428']:
                allWorklogs[str(issue)]['Software'] = self.jiraService.issue(str(issue)).raw['fields']['customfield_11428']['value']
            
            if self.jiraService.issue(str(issue)).raw['fields']['customfield_11414']:
                allWorklogs[str(issue)]['Component'] = self.jiraService.issue(str(issue)).raw['fields']['customfield_11414']['value']
            
            if self.jiraService.issue(str(issue)).raw['fields']['customfield_11410']:
                allWorklogs[str(issue)]['Story Point'] = self.jiraService.issue(str(issue)).raw['fields']['customfield_11410']

            if self.jiraService.issue(str(issue)).raw['fields']['status']['name'] == 'Done':
                allWorklogs[str(issue)]['Date Finished'] = self.jiraService.issue(str(issue)).raw['fields']['statuscategorychangedate'][:10]

            allWorklogs[str(issue)]['Date Started'] = self.jiraService.issue(str(issue)).raw['fields']['worklog']['worklogs'][0]['started'][:10]
            
        # Returns a list of Worklogs
        return allWorklogs

    def queryAdhocItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f'{WORKLOG_DATE} AND assignee in ({MEMBERS[person]}) AND project = {PROJECT} AND issuetype = Ad-hoc AND Sprint in {SPRINT}',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs
    
    def queryProjectItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f'{WORKLOG_DATE} AND assignee in ({MEMBERS[person]}) AND project = {PROJECT} AND issuetype != Ad-hoc AND Sprint in {SPRINT}',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

    def queryJIRA(self, memberToQuery, swToQuery):
        allIssues = self.jiraService.search_issues(
            f'{WORKLOG_DATE} AND assignee in ({MEMBERS[memberToQuery]}) AND project = {PROJECT} AND Sprint in {SPRINT} AND "Software[Dropdown]" = \"{swToQuery}\"',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

# This class is responsible for querying each of the
# PROJECT items belonging to the various SW
class TimeSpentPerSoftware(object):
    def __init__(self) -> None:
        super().__init__()
        self.software = {}
        self.worklogsForEachSW = WorkLogsForEachSW()
        getDesiredSprintYearAndMonth()

    def extractItemsPerSW(self, person, jIRAService):
        self.software[person] = {}
        for sw in SOFTWARE:
            self.software[person][sw] = jIRAService.queryJIRA(person, sw)

    def getTimeSpentForEachSW(self, person):
        return self.worklogsForEachSW.getWorkLogsForEachSW(self.software[person], person)

# Multithreaded Class for MatrixOfWorklogsPerSW
class ThreadHoursSpentPerSW(threading.Thread):
    def __init__(self, person, jiraService, worklog, timeSpentPerSoftware):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.worklog = worklog
        self.timeSpentPerSoftware = timeSpentPerSoftware

    def run(self):
        self.timeSpentPerSoftware.extractItemsPerSW(self.person, self.jiraService)
        self.worklog[self.person] = self.timeSpentPerSoftware.getTimeSpentForEachSW(self.person)
        print(f'Finished Getting Hours Spent for Each SW for: {self.person}')

# This will be the "Caller" class
class HoursSpentPerSW(object):
    def __init__(self, jiraService) -> None:
        super().__init__()
        self.jiraService = jiraService
        self.result = []
        self.worklog = {}

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

    def extractTimeSpentPerSW(self):
        timeSpentPerSoftware = TimeSpentPerSoftware()

        print("\n-------- GENERATING MATRIX OF TIME SPENT PER SW --------\n")

        for person in MEMBERS:
            self.worklog[person] = {}

        threads = [ThreadHoursSpentPerSW(
                person, self.jiraService, self.worklog, timeSpentPerSoftware) for person in MEMBERS]

        for thread in threads:
            thread.setDaemon(True)
            thread.start()

        for thread in threads:
            thread.join()

        self.__cleanWorklogs__()

    def __cleanWorklogs__(self):
        tempWorklog = {}
        for person in MEMBERS:
            tempWorklog[person] = self.worklog[person][person]

        # Formatting the data before writing to CSV
        tempData = list(tempWorklog.values())
        subset = set()
        for element in tempData:
            for index in element:
                subset.add(index)
        tempResult = []
        tempResult.append(subset)
        for key, value in tempWorklog.items():
            tempData2 = []
            for index in subset:
                tempData2.append(value.get(index, 0))
            tempResult.append(tempData2)

        self.result = [[index for index, value in tempWorklog.items()]] + \
            list(map(list, zip(*tempResult)))

    def writeToCSVFile(self):
        if len(self.result) != 0:
            self.__getTotal__()
            fileName = input("Filename for Hours Spent per SW: ")
            self.result[0].insert(0, 'SW Names')

            # Putting "Total" at the last column
            self.result[0].insert(len(MEMBERS) + 1, 'Total')

            # Putting "Total" at the last row
            self.result[-1].insert(0, 'Total')
            self.result[-1].pop(1)
            
            df = pd.DataFrame(self.result)
            df.to_csv(fileName, index=False, header=False)
            print(f"Writing to {fileName} done.")
        else:
            print("You need to call MatrixOfWorklogsPerSW.generateMatrix() first.")
            exit(1)

class AutoVivification(dict):
    """Implementation of perl's autovivification feature."""
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

# Multithreaded Class for ThreadRawItemsPerPerson
class ThreadRawItemsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, itemsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.itemsPerPerson = itemsPerPerson

    def run(self):
        self.itemsPerPerson[self.person] = self.jiraService.queryRawItemsPerPerson(self.person)
        print(f'Finished Getting Raw Items For: {self.person}')

class RawItemsPerPerson(object):
    def __init__(self, jiraService) -> None:
        super().__init__()
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.personKey = None
        self.timeHelper = TimeHelper()
        self.itemsPerPerson = AutoVivification()
        self.worklogPerPerson = AutoVivification()
    
    def __extractRawItemsPerPerson__(self):
        print("\n-------- GENERATING MATRIX OF RAW ITEMS PER PERSON --------\n")
        
        for person in MEMBERS:
            self.itemsPerPerson[person] = {}

        threads = [ThreadRawItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in MEMBERS]

        for thread in threads:
            thread.setDaemon(True)
            thread.start()

        for thread in threads:
            thread.join()

        return self.itemsPerPerson

    def __computeRawItemsPerPerson__(
        self, logsPerValue, person, jiraID, description, software,
        component, storyPoint, dateStarted, dateFinished):
        
        if self.personKey != person:
            self.worklogPerPerson[person] = {}
            self.personKey = person

        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[person][jiraID] = {}
            self.worklogPerPerson[person][jiraID]['description'] = description
            self.worklogPerPerson[person][jiraID]['Software'] = software
            self.worklogPerPerson[person][jiraID]['Component'] = component
            self.worklogPerPerson[person][jiraID]['Story Point'] = storyPoint
            self.worklogPerPerson[person][jiraID]['Date Started'] = dateStarted
            self.worklogPerPerson[person][jiraID]['Date Finished'] = dateFinished
            self.worklogPerPerson[person][jiraID]['timeSpent'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue)
        if extractedDateTime:
            if extractedDateTime.month == DESIRED_MONTH and extractedDateTime.year == DESIRED_YEAR:
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerPerson[person][jiraID]['timeSpent'] += timeSpent

    def extractRawItemsPerPerson(self):
        getDesiredSprintYearAndMonth()
        allWorklogs = self.__extractRawItemsPerPerson__()
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:
                for worklogPerJIRAId in allWorklogs[person][jiraID]['timeSpent']:
                    description = allWorklogs[person][jiraID]['description']
                    software = allWorklogs[person][jiraID]['Software']
                    component = allWorklogs[person][jiraID]['Component']
                    storyPoint = allWorklogs[person][jiraID]['Story Point']
                    dateStarted = allWorklogs[person][jiraID]['Date Started']
                    dateFinished = allWorklogs[person][jiraID]['Date Finished']
                    
                    self.__computeRawItemsPerPerson__(
                        worklogPerJIRAId, person, jiraID, description, software, component, storyPoint,
                        dateStarted, dateFinished)

    def generateCSVFile(self):
        fileName = input("Filename for Raw Items Per Person: ")
        
        with open(fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            for person in self.worklogPerPerson:
                csvwriter.writerow([person])
                for jiraID in self.worklogPerPerson[person]:
                    csvwriter.writerow([jiraID, 
                        self.worklogPerPerson[person][jiraID]['description'],
                        self.worklogPerPerson[person][jiraID]['Software'],
                        self.worklogPerPerson[person][jiraID]['Component'],
                        self.worklogPerPerson[person][jiraID]['Story Point'],
                        self.worklogPerPerson[person][jiraID]['Date Started'],
                        self.worklogPerPerson[person][jiraID]['Date Finished'],
                        self.worklogPerPerson[person][jiraID]['timeSpent']])
        
        print(f"Writing to {fileName} done.")

# Multithreaded Class for ThreadDoneItemsPerPerson
class ThreadDoneItemsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, itemsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.itemsPerPerson = itemsPerPerson

    def run(self):
        self.itemsPerPerson[self.person] = self.jiraService.queryNumberOfDoneItemsPerPerson(self.person)
        print(f'Finished Getting Done Items For: {self.person}')

class DoneItemsPerPerson(object):
    def __init__(self, jiraService) -> None:
        super().__init__()
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.timeHelper = TimeHelper()
        self.itemsPerPerson = AutoVivification()
        self.worklogPerPerson = AutoVivification()
    
    def __extractDoneItemsPerPerson__(self):
        print("\n-------- GENERATING MATRIX OF DONE ITEMS PER PERSON --------\n")

        for person in MEMBERS:
            self.itemsPerPerson[person] = {}

        threads = [ThreadDoneItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in MEMBERS]

        for thread in threads:
            thread.setDaemon(True)
            thread.start()

        for thread in threads:
            thread.join()
        
        return self.itemsPerPerson

    def __computeDoneItemsPerPerson__(self, logsPerValue, person, jiraID, description):
        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[person][jiraID] = {}
            self.worklogPerPerson[person][jiraID]['description'] = description
            self.worklogPerPerson[person][jiraID]['timeSpent'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue)
        if extractedDateTime:
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerPerson[person][jiraID]['timeSpent'] += timeSpent

    def extractDoneItemsPerPerson(self):
        getDesiredSprintYearAndMonth()
        allWorklogs = self.__extractDoneItemsPerPerson__()
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:                
                if not allWorklogs[person][jiraID]['timeSpent']:
                    self.worklogPerPerson[person][jiraID] = {}
                    self.worklogPerPerson[person][jiraID]['description'] = allWorklogs[person][jiraID]['description']
                    self.worklogPerPerson[person][jiraID]['timeSpent'] = 0
                
                for worklogPerJIRAId in allWorklogs[person][jiraID]['timeSpent']:
                    description = allWorklogs[person][jiraID]['description']
                    self.__computeDoneItemsPerPerson__(worklogPerJIRAId, person, jiraID, description)

    def generateCSVFile(self):
        fileName = input("Filename for Done Items Per Person: ")
        
        with open(fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            for person in self.worklogPerPerson:
                csvwriter.writerow([person])
                for jiraID in self.worklogPerPerson[person]:
                    csvwriter.writerow([jiraID, self.worklogPerPerson[person][jiraID]['description'],
                                        self.worklogPerPerson[person][jiraID]['timeSpent']])
        
        print(f"Writing to {fileName} done.")

# Multithreaded Class for ThreaditemsPerPerson
class ThreadItemsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, itemsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.itemsPerPerson = itemsPerPerson

    def run(self):
        for issueType in ISSUE_TYPES:
            if issueType == 'Project':
                self.itemsPerPerson[self.person][issueType] = self.jiraService.queryProjectItemsPerPerson(self.person)
            elif issueType == 'Ad-hoc':
                self.itemsPerPerson[self.person][issueType] = self.jiraService.queryAdhocItemsPerPerson(self.person)
        
        print(f'Finished Getting Time Spent For: {self.person}')

class TimeSpentPerPerson(object):
    def __init__(self, jiraService) -> None:
        super().__init__()
        self.jiraService = jiraService
        self.issueId = None
        self.issueTypeKey = None
        self.personKey = None
        self.timeHelper = TimeHelper()
        self.itemsPerPerson = AutoVivification()
        self.worklogPerPerson = AutoVivification()

    def __extractItemsPerPerson__(self):
        print("\n-------- GENERATING MATRIX OF TIME SPENT PER PERSON --------\n")

        for person in MEMBERS:
            self.itemsPerPerson[person] = {}

        threads = [ThreadItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in MEMBERS]

        for thread in threads:
            thread.setDaemon(True)
            thread.start()

        for thread in threads:
            thread.join()
        
        return self.itemsPerPerson

    def __extractTime__(self, logsPerValue, person, issueType):
        if self.personKey != person:
            self.worklogPerPerson[person] = {}
            self.personKey = person

        if self.issueTypeKey != issueType:
            self.issueTypeKey = issueType
            self.worklogPerPerson[person][issueType] = 0

        extractedDateTime = self.timeHelper.trimDate(logsPerValue)
        if extractedDateTime:
            if extractedDateTime.month == DESIRED_MONTH and extractedDateTime.year == DESIRED_YEAR:
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerPerson[person][issueType] += timeSpent

    def extractTimeSpentPerPerson(self):
        getDesiredSprintYearAndMonth()
        allWorklogs = self.__extractItemsPerPerson__()
        for person in allWorklogs:
            self.issueTypeKey = None
            for issueType in ISSUE_TYPES:
                for jiraID in allWorklogs[person][issueType]:
                    for worklogPerJIRAId in allWorklogs[person][issueType][jiraID]:
                        self.__extractTime__(worklogPerJIRAId, person, issueType)

    def generateCSVFile(self):
        df = pd.DataFrame(self.worklogPerPerson)
        fileName = input("Filename for Time Spent Per Person: ")
        df.to_csv(fileName, index=True, header=MEMBERS.keys())
        print(f"Writing to {fileName} done.")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    jiraService = JIRAService()

    # matrixOfWorklogsPerSW = HoursSpentPerSW(jiraService)
    # matrixOfWorklogsPerSW.extractTimeSpentPerSW()
    # matrixOfWorklogsPerSW.writeToCSVFile()

    # timeSpentPerPerson = TimeSpentPerPerson(jiraService)
    # timeSpentPerPerson.extractTimeSpentPerPerson()
    # timeSpentPerPerson.generateCSVFile()

    doneItemsPerPerson = DoneItemsPerPerson(jiraService)
    doneItemsPerPerson.extractDoneItemsPerPerson()
    doneItemsPerPerson.generateCSVFile()

    # rawItemsPerPerson = RawItemsPerPerson(jiraService)
    # rawItemsPerPerson.extractRawItemsPerPerson()
    # rawItemsPerPerson.generateCSVFile()

if __name__ == "__main__":
    main()
