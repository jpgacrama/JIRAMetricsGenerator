import pandas as pd
import os
import threading
from Helpers import AutoVivification, TimeHelper

ISSUE_TYPES = ['Project', 'Ad-hoc']

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
        
class TimeSpentPerPerson:
    def __init__(
            self,
            jiraService,
            desiredMonth,
            desiredYear,
            members,
            fileName,
            outputFolder) -> None:
        self.jiraService = jiraService
        self.issueId = None
        self.issueTypeKey = None
        self.personKey = None
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear
        self.members = members
        self.fileName = fileName
        self.outputFolder = outputFolder
        self.timeHelper = TimeHelper.TimeHelper()
        self.itemsPerPerson = AutoVivification.AutoVivification()
        self.worklogPerPerson = AutoVivification.AutoVivification()

    def __extractTimeSpentPerPerson__(self, progressBarTimeSpentPerPerson):
        print("\n-------- GENERATING MATRIX OF TIME SPENT PER PERSON --------\n")

        for person in self.members:
            self.itemsPerPerson[person] = {}

        threads = [ThreadItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in self.members]

        for thread in threads:
            thread.start()

        i = 0
        numberOfPeople = len(self.members)
        for thread in threads:
            thread.join()
            i += 1
            progressBarTimeSpentPerPerson.update_bar(i, numberOfPeople - 1)
        
        return self.itemsPerPerson

    def __extractTime__(self, logsPerValue, person, issueType):
        if self.personKey != person:
            self.worklogPerPerson[person] = {}
            self.personKey = person

        if self.issueTypeKey != issueType:
            self.issueTypeKey = issueType
            self.worklogPerPerson[person][issueType] = 0

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            if extractedDateTime.month == self.desiredMonth and extractedDateTime.year == self.desiredYear:
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerPerson[person][issueType] += timeSpent

    async def extractTimeSpentPerPerson(self, progressBarTimeSpentPerPerson):
        allWorklogs = self.__extractTimeSpentPerPerson__(progressBarTimeSpentPerPerson)
        for person in allWorklogs:
            self.issueTypeKey = None
            for issueType in ISSUE_TYPES:
                for jiraID in allWorklogs[person][issueType]:
                    for worklogPerJIRAId in allWorklogs[person][issueType][jiraID]:
                        self.__extractTime__(worklogPerJIRAId, person, issueType)

        self.__generateCSVFile__()

    def __generateCSVFile__(self):
        df = pd.DataFrame(self.worklogPerPerson)
        os.makedirs(self.outputFolder, exist_ok=True) 
        df.to_csv(self.outputFolder + self.fileName, index=True, header=self.members.keys())
        print(f"Writing to {self.fileName} done.")

