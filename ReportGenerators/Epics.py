import threading
import csv
import os
from Helpers import TimeHelper, AutoVivification

class OneThreadPerChild(threading.Thread):
    def __init__(self, key, value, month, year, timeHelper, parentKey, worklogFromMainThread):
        threading.Thread.__init__(self)
        self.key = key
        self.value = value
        self.desiredMonth = month
        self.desiredYear = year
        self.timeHelper = timeHelper
        self.childWorklog = AutoVivification.AutoVivification()   
        self.parent = worklogFromMainThread
        self.parentKey = parentKey    
        
        self.childWorklog['description'] = self.value['description']
        self.childWorklog['Hours Spent for the Month'] = 0
        self.childWorklog['Total Hours Spent'] = 0

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
                    self.childWorklog['Hours Spent for the Month'] += timeSpent

                # For Total Hours Spent
                timeSpent = worklog.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.childWorklog['Total Hours Spent'] += timeSpent

        # Passing out the results to the calling thread
        if self.childWorklog:
            self.parent[self.parentKey][self.key] = self.childWorklog
            pass

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
        self.worklogsOfChild = AutoVivification.AutoVivification()

    def __extractEpics__ (self):
        print("\n-------- GENERATING MATRIX OF EPICS --------\n")

        epicThread = []
        for epic in self.epics:
            exclude_keys = ['description']
            parentDictionary = self.epics[epic]
            print(f'CALLING CLASS: Parent Key: {epic}')
            
            childrenDictionary = {k: parentDictionary[k] for k in set(list(parentDictionary.keys())) - set(exclude_keys)}
            
            self.worklogsOfChild[epic] = {}
            epicThread.append([OneThreadPerChild(
                    key, value,
                    self.desiredMonth,
                    self.desiredYear,
                    self.timeHelper,
                    epic,
                    self.worklogsOfChild)
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

        # TODO: I don't think this is a good idea
        # when we have multiple epics to count
        epicAndComputedChildren = {}
        for epic in self.epics:
            epicAndComputedChildren[epic] = {
                'description': self.epics[epic]['description'],
                'number of children': len(self.worklogsOfChild),
                'children': self.worklogsOfChild}

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

            for parent in dictionary:
                csvwriter.writerow([
                    f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{parent}\"),\"{parent}\")',
                    '',
                    dictionary[parent]['description']                    
                ])
                for child in dictionary[parent]['children']:
                    if dictionary[parent]['children'][child]:
                        csvwriter.writerow([
                            f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{parent}\"),\"{parent}\")',
                            f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{child}\"),\"{child}\")',                        
                            dictionary[parent]['children'][child]['description'],
                            dictionary[parent]['children'][child]['Hours Spent for the Month'],
                            dictionary[parent]['children'][child]['Total Hours Spent']])
                
        print(f"Writing to {self.fileName} done.")

