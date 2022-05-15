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
        print(f'\tTHREAD: Child Key being processed: {self.key}')
        
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

class Epics:
    def __init__(
            self,
            jiraService,
            desiredMonth,
            desiredYear,
            fileName,
            outputFolder,
            progressBar) -> None:
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.fileName = fileName
        self.outputFolder = outputFolder
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear
        self.timeHelper = TimeHelper.TimeHelper()
        self.epics = self.jiraService.queryEpics(progressBar)
        self.worklogPerChild = AutoVivification.AutoVivification()

    def __extractEpics__ (self):
        print("\n-------- GENERATING MATRIX OF EPICS --------\n")

        epicThread = []
        for epic in self.epics:
            exclude_keys = ['description']
            parentDictionary = self.epics[epic]
            print(f'CALLING CLASS: Parent Key: {epic}')
            
            childrenDictionary = {k: parentDictionary[k] for k in set(list(parentDictionary.keys())) - set(exclude_keys)}
            
            epicThread.append([OneThreadPerChild(
                    key, value,
                    self.desiredMonth,
                    self.desiredYear,
                    self.timeHelper,
                    self.worklogPerChild)
                for key, value in childrenDictionary.items()])

            print(f'\tFinished creating a total of {len(epicThread)} children threads')
        
        for thread in epicThread:
            for childThread in thread:
                childThread.start()

        for thread in epicThread:
            for childThread in thread:
                childThread.join()

        # Adding Computed Child values back to parent epic
        # First entry is ALWAYS the PARENT
        epicAndComputedChildren = {}
        for epic in self.epics:
            epicAndComputedChildren[epic] = {
                'number of children': len(self.worklogPerChild),
                'description': self.epics[epic]['description']}
            epicAndComputedChildren.update(self.worklogPerChild)

        return epicAndComputedChildren
    
    async def extractEpics(self):
        dictionary = self.__extractEpics__()
        self.__generateCSVFile__(dictionary)

    def __generateCSVFile__(self, dictionary):
        os.makedirs(self.outputFolder, exist_ok=True) 
        with open(self.outputFolder + self.fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['Parent Epic ID','Child ID', 'Description', 'Hours Spent for the Month', 'Total Hours Spent'])

            isParent = True
            childCount = 0
            numberOfChildren = 0
            for item in dictionary:
                if childCount == numberOfChildren:
                    # Next entry is again a parent
                    isParent = True
                
                if isParent:
                    # Next entry will now be a child
                    isParent = False
                    numberOfChildren = dictionary[item]['number of children']
                    parent = f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{item}\"),\"{item}\")'
                    csvwriter.writerow([
                        parent,
                        '',
                        dictionary[item]['description']                    
                    ])
                else:
                    csvwriter.writerow([
                        parent,
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{item}\"),\"{item}\")',                        
                        dictionary[item]['description'],
                        dictionary[item]['Hours Spent for the Month'],
                        dictionary[item]['Total Hours Spent']])
                    childCount += 1
                
        print(f"Writing to {self.fileName} done.")

