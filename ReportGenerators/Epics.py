import csv
import os
from Helpers import TimeHelper, AutoVivification

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
        self.worklogPerPerson = AutoVivification.AutoVivification()

    def __computeTimeSpentPerEpic__(self, logsPerValue, jiraID, description):
        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[jiraID] = {}
            self.worklogPerPerson[jiraID]['description'] = description
            self.worklogPerPerson[jiraID]['Total Hours Spent'] = 0
            self.worklogPerPerson[jiraID]['Hours Spent for the Month'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            # For Hours Spent for the Current Month
            if extractedDateTime.month == self.desiredMonth and extractedDateTime.year == self.desiredYear:
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerPerson[jiraID]['Hours Spent for the Month'] += timeSpent
            
            # For Total Hours Spent
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerPerson[jiraID]['Total Hours Spent'] += timeSpent

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

        self.__generateCSVFile__()

    def __generateCSVFile__(self):
        os.makedirs(self.outputFolder, exist_ok=True) 
        with open(self.outputFolder + self.fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['Name', 'JIRA ID', 'Description', 'Hours Spent'])

            for person in self.worklogPerPerson:
                for jiraID in self.worklogPerPerson[person]:
                    csvwriter.writerow([
                        person,
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{jiraID}\"),\"{jiraID}\")',                        
                        self.worklogPerPerson[person][jiraID]['description'],
                        self.worklogPerPerson[person][jiraID]['Total Hours Spent']])
        
        print(f"Writing to {self.fileName} done.")

