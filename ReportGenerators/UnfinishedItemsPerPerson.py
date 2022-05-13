import threading
import csv
import os
from Helpers import TimeHelper, AutoVivification

# Multithreaded Class for ThreadUnfinishedItemsPerPerson
class ThreadUnfinishedItemsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, itemsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.itemsPerPerson = itemsPerPerson

    def run(self):
        self.itemsPerPerson[self.person] = self.jiraService.queryNumberOfUnfinishedItemsPerPerson(self.person)

class UnfinishedItemsPerPerson:
    def __init__(
            self,
            jiraService,
            members,
            fileName,
            outputFolder) -> None:
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.members = members
        self.fileName = fileName
        self.outputFolder = outputFolder
        self.timeHelper = TimeHelper.TimeHelper()
        self.itemsPerPerson = AutoVivification.AutoVivification()
        self.worklogPerPerson = AutoVivification.AutoVivification()
    
    def __extractUnfinishedItemsPerPerson__(self, progressBarUnfinishedItemsPerPerson):
        print("\n-------- GENERATING MATRIX OF UNFINISHED ITEMS PER PERSON --------\n")

        for person in self.members:
            self.itemsPerPerson[person] = {}

        threads = [ThreadUnfinishedItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in self.members]

        for thread in threads:
            thread.start()

        i = 0
        numberOfPeople = len(self.members)
        for thread in threads:
            thread.join()
            i += 1
            progressBarUnfinishedItemsPerPerson.update_bar(i, numberOfPeople - 1)

        return self.itemsPerPerson

    def __computeUnfinishedItemsPerPerson__(self, logsPerValue, person, jiraID, description):
        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[person][jiraID] = {}
            self.worklogPerPerson[person][jiraID]['description'] = description
            self.worklogPerPerson[person][jiraID]['Total Hours Spent'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerPerson[person][jiraID]['Total Hours Spent'] += timeSpent

    async def extractUnfinishedItemsPerPerson(self, progressBarUnfinishedItemsPerPerson):
        allWorklogs = self.__extractUnfinishedItemsPerPerson__(progressBarUnfinishedItemsPerPerson)
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:                
                if not allWorklogs[person][jiraID]['Total Hours Spent']:
                    self.worklogPerPerson[person][jiraID] = {}
                    self.worklogPerPerson[person][jiraID]['description'] = allWorklogs[person][jiraID]['description']
                    self.worklogPerPerson[person][jiraID]['Total Hours Spent'] = 0
                
                for worklogPerJIRAId in allWorklogs[person][jiraID]['Total Hours Spent']:
                    description = allWorklogs[person][jiraID]['description']
                    self.__computeUnfinishedItemsPerPerson__(worklogPerJIRAId, person, jiraID, description)

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

