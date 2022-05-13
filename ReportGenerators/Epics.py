import csv
import os
from Helpers import TimeHelper, AutoVivification

# Python code to merge dictionaries using a single
# expression
def Merge(dict1, dict2):
    res = {**dict1, **dict2}
    return res

class Epics:
    def __init__(
            self,
            jiraService,
            desiredMonth,
            desiredYear,
            fileName,
            outputFolder) -> None:
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.fileName = fileName
        self.outputFolder = outputFolder
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear
        self.timeHelper = TimeHelper.TimeHelper()
        self.epics = self.jiraService.queryEpics()
        self.worklogPerEpic = AutoVivification.AutoVivification()

    def __computeTimeSpentPerEpic__(self, logsPerValue, jiraID, description):
        if self.jiraIDKey != jiraID:
            self.worklogPerEpic[jiraID] = {}
            self.worklogPerEpic[jiraID]['description'] = description
            self.worklogPerEpic[jiraID]['Hours Spent for the Month'] = 0
            self.worklogPerEpic[jiraID]['Total Hours Spent'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            # For Hours Spent for the Current Month
            if extractedDateTime.month == self.desiredMonth and extractedDateTime.year == self.desiredYear:
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerEpic[jiraID]['Hours Spent for the Month'] += timeSpent
            
            # For Total Hours Spent
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerEpic[jiraID]['Total Hours Spent'] += timeSpent

    def extractEpics(self, progressBarEpics):
        print("\n-------- GENERATING MATRIX OF EPICS --------\n")

        for epic in self.epics:
            for child in self.epics[epic]:                
                exclude_keys = ['description']
                parentDictionary = self.epics[epic]
                childrenDictionary = {k: parentDictionary[k] for k in set(list(parentDictionary.keys())) - set(exclude_keys)}
                
                for child in childrenDictionary:
                    for worklog in childrenDictionary[child]['Total Hours Spent']:
                        description = childrenDictionary[child]['description']
                        self.__computeTimeSpentPerEpic__(worklog, child, description)

                # Re-attach Children to parent
                combinedDictionary = {list(self.epics.keys())[0]: self.worklogPerEpic}

        self.__generateCSVFile__()

    def __generateCSVFile__(self):
        os.makedirs(self.outputFolder, exist_ok=True) 
        with open(self.outputFolder + self.fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['Name', 'JIRA ID', 'Description', 'Hours Spent'])

            for item in self.worklogPerEpic:
                csvwriter.writerow([
                    item,
                    f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{jiraID}\"),\"{jiraID}\")',                        
                    self.worklogPerEpic[item][jiraID]['description'],
                    self.worklogPerEpic[item][jiraID]['Total Hours Spent']])
        
        print(f"Writing to {self.fileName} done.")

