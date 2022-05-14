import threading
import csv
import os
from Helpers import TimeHelper, AutoVivification

class OneThreadPerEpic(threading.Thread):
    def __init__(self, key, value, month, year, timeHelper, worklogPerEpic):
        threading.Thread.__init__(self)
        self.key = key
        self.value = value
        self.desiredMonth = month
        self.desiredYear = year
        self.timeHelper = timeHelper
        self.worklogPerEpic = worklogPerEpic
        
        
        self.worklogPerEpic['description'] = self.value['description']
        self.worklogPerEpic['Hours Spent for the Month'] = 0
        self.worklogPerEpic['Total Hours Spent'] = 0

    def run(self):
        # Get time started
        for worklog in self.value['Total Hours Spent']:
            timeSpent = 0
            extractedDateTime = self.timeHelper.trimDate(worklog.started)
            
            if extractedDateTime:
                # For Hours Spent for the Current Month
                if extractedDateTime.month == self.desiredMonth and extractedDateTime.year == self.desiredYear:
                    timeSpent = worklog.timeSpentSeconds
                    timeSpent = self.timeHelper.convertToHours(timeSpent)
                    self.worklogPerEpic['Hours Spent for the Month'] += timeSpent

                # For Total Hours Spent
                timeSpent = worklog.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerEpic['Total Hours Spent'] += timeSpent

        print(f'Finished computing{self.key}. Consider passing the result to calling thread')

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

    def __extractEpics__ (self, progressBar):
        print("\n-------- GENERATING MATRIX OF EPICS --------\n")

        for epic in self.epics:
            exclude_keys = ['description']
            parentDictionary = self.epics[epic]
            childrenDictionary = {k: parentDictionary[k] for k in set(list(parentDictionary.keys())) - set(exclude_keys)}
            
            threads = [OneThreadPerEpic(
                    key, value,
                    self.desiredMonth,
                    self.desiredYear,
                    self.timeHelper,
                    self.worklogPerEpic)
                for key, value in childrenDictionary.items()]
        
        for thread in threads:
            thread.start()

        i = 0
        numberOfEpics = len(self.epics)
        for thread in threads:
            thread.join()
            i += 1
            progressBar.update_bar(i, numberOfEpics - 1)
    
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

    async def extractEpics(self, progressBarEpics):
        self.__extractEpics__(progressBarEpics)

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

        self.__generateCSVFile__(combinedDictionary)

    def __generateCSVFile__(self, combinedDictionary):
        os.makedirs(self.outputFolder, exist_ok=True) 
        with open(self.outputFolder + self.fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['Parent Epic ID','Child ID', 'Description', 'Hours Spent for the Month', 'Total Hours Spent'])

            i = 0
            for item in combinedDictionary:
                if not i:
                    csvwriter.writerow([
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{item}\"),\"{item}\")',                        
                    ])
                else:
                    csvwriter.writerow([
                        item,
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{jiraID}\"),\"{jiraID}\")',                        
                        self.worklogPerEpic[item][jiraID]['description'],
                        self.worklogPerEpic[item][jiraID]['Total Hours Spent']])
                i += 1
        
        print(f"Writing to {self.fileName} done.")

