import threading
import csv
import os
from Helpers import TimeHelper, AutoVivification

# Multithreaded Class for ThreadUnfinishedItemsPerPerson
class ThreadEpicsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, epicsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.epicsPerPerson = epicsPerPerson

    def run(self):
        self.epicsPerPerson[self.person] = self.jiraService.queryNumberOfEpicsPerPerson(self.person)

class EpicsPerPerson:
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
    
    def __extractEpicsPerPerson__(self, progressBarEpicsPerPerson):
        print("\n-------- GENERATING MATRIX OF EPICS PER PERSON --------\n")

        for person in self.members:
            self.itemsPerPerson[person] = {}

        threads = [ThreadEpicsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in self.members]

        for thread in threads:
            thread.start()

        i = 0
        numberOfPeople = len(self.members)
        for thread in threads:
            thread.join()
            i += 1
            progressBarEpicsPerPerson.update_bar(i, numberOfPeople - 1)

        return self.itemsPerPerson

    def __computeEpicsPerPerson__(self, logsPerValue, jiraID, description):
        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[jiraID] = {}
            self.worklogPerPerson[jiraID]['description'] = description
            self.worklogPerPerson[jiraID]['Total Hours Spent'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerPerson[jiraID]['Total Hours Spent'] += timeSpent

    async def extractEpicsPerPerson(self, progressBarUnfinishedItemsPerPerson):
        allWorklogs = self.__extractEpicsPerPerson__(progressBarUnfinishedItemsPerPerson)
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:                
                exclude_keys = ['description']
                parentDictionary = allWorklogs[person][jiraID]
                childrenDictionary = {k: parentDictionary[k] for k in set(list(parentDictionary.keys())) - set(exclude_keys)}
                
                for child in childrenDictionary:
                    for worklog in childrenDictionary[child]['Total Hours Spent']:
                        description = childrenDictionary[child]['description']
                        self.__computeEpicsPerPerson__(worklog, child, description)
                        pass

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

