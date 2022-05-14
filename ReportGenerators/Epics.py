import threading
import csv
import os
from Helpers import TimeHelper, AutoVivification

class OneThreadPerChild(threading.Thread):
    def __init__(self, key, value, month, year, timeHelper, parent):
        threading.Thread.__init__(self)
        self.key = key
        self.value = value
        self.desiredMonth = month
        self.desiredYear = year
        self.timeHelper = timeHelper
        self.worklog = AutoVivification.AutoVivification()   
        self.parent = parent     
        
        self.worklog['description'] = self.value['description']
        self.worklog['Hours Spent for the Month'] = 0
        self.worklog['Total Hours Spent'] = 0

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
                    self.worklog['Hours Spent for the Month'] += timeSpent

                # For Total Hours Spent
                timeSpent = worklog.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklog['Total Hours Spent'] += timeSpent

        # Passing out the results to the calling thread
        self.parent[self.key] = self.worklog
        print(f'\nINSIDE THREAD {self.key}: PARENT: {self.parent}')

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
        self.worklogPerChild = AutoVivification.AutoVivification()

    def __extractEpics__ (self, progressBar):
        print("\n-------- GENERATING MATRIX OF EPICS --------\n")

        for epic in self.epics:
            exclude_keys = ['description']
            parentDictionary = self.epics[epic]
            childrenDictionary = {k: parentDictionary[k] for k in set(list(parentDictionary.keys())) - set(exclude_keys)}
            
            threads = [OneThreadPerChild(
                    key, value,
                    self.desiredMonth,
                    self.desiredYear,
                    self.timeHelper,
                    self.worklogPerChild)
                for key, value in childrenDictionary.items()]
        
        for thread in threads:
            thread.start()

        i = 0
        numberOfThreads = len(threads)
        for thread in threads:
            thread.join()
            i += 1
            progressBar.update_bar(i, numberOfThreads - 1)

        # Adding Computed Child values back to parent epic
        # First entry is ALWAYS the PARENT
        self.epicAndComputedChildren = {}
        for epic in self.epics:
            self.epicAndComputedChildren[epic] = self.epics[epic]['description']
            self.epicAndComputedChildren.update(self.worklogPerChild)
            print(f'{self.epicAndComputedChildren[epic]}')
    
    async def extractEpics(self, progressBarEpics):
        self.__extractEpics__(progressBarEpics)
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
                        self.worklogPerChild[item][jiraID]['description'],
                        self.worklogPerChild[item][jiraID]['Total Hours Spent']])
                i += 1
        
        print(f"Writing to {self.fileName} done.")

