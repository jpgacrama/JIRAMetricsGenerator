import threading
import csv
import os
from Helpers import TimeHelper, AutoVivification

class OneThreadPerChild(threading.Thread):
    def __init__(self, key, value, month, year, timeHelper, worklogFromMainThread):
        threading.Thread.__init__(self)
        self.key = key
        self.value = value
        self.desiredMonth = month
        self.desiredYear = year
        self.timeHelper = timeHelper
        self.worklog = worklogFromMainThread # Value to be mutated   

    def run(self): 
        # Get time started
        self.worklog[self.key]['Hours Spent for the Month'] = 0
        self.worklog[self.key]['Total Hours Spent'] = 0
        for worklog in self.value['Total Hours Spent']:
            timeSpent = 0
            extractedDateTime = self.timeHelper.trimDate(worklog.started)
            if extractedDateTime:
                # For Hours Spent for the Current Month
                if (extractedDateTime.month == self.desiredMonth and
                    extractedDateTime.year == self.desiredYear):
                    
                    timeSpent = worklog.timeSpentSeconds
                    timeSpent = self.timeHelper.convertToHours(timeSpent)
                    self.worklog[self.key]['Hours Spent for the Month'] += timeSpent

                # For Total Hours Spent
                timeSpent = worklog.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)                
                self.worklog[self.key]['Total Hours Spent'] += timeSpent

class OperationalItems:
    def __init__(
            self,
            jiraService,
            desiredMonth,
            desiredYear,
            fileName,
            outputFolder,
            progressBar) -> None:
        self.jiraService = jiraService
        self.fileName = fileName
        self.outputFolder = outputFolder
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear
        self.timeHelper = TimeHelper.TimeHelper()
        self.operationalItems = self.jiraService.queryAllOperationalTicketsNotUnderAnEpic(progressBar)
        self.worklogs = AutoVivification.AutoVivification()

    def __extractOperationalItems__ (self):
        print("\n-------- GENERATING MATRIX OF OPERATIONAL ITEMS --------\n")

        operationalItemsThread = []
        for item in self.operationalItems:
            self.worklogs[item] = {}
            self.worklogs[item]['is production support'] = self.operationalItems[item]['is production support']
            self.worklogs[item]['description'] = self.operationalItems[item]['description']
            operationalItemsThread.append([OneThreadPerChild(
                    key,
                    value,
                    self.desiredMonth,
                    self.desiredYear,
                    self.timeHelper,
                    self.worklogs)
                for key, value in self.operationalItems.items()])

        for thread in operationalItemsThread:
            for childThread in thread:
                childThread.start()

        for thread in operationalItemsThread:
            for childThread in thread:
                childThread.join()
    
    async def extractOperationalItems(self):
        self.__extractOperationalItems__()
        self.__generateCSVFile__()

    def __generateCSVFile__(self):
        os.makedirs(self.outputFolder, exist_ok=True) 
        with open(self.outputFolder + self.fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['JIRA ID', 'Is production support', 'Description',
                'Hours Spent for the Month', 'Total Hours Spent'])

            for jiraID in self.worklogs:
                if set(('is production support', 'description', 'Total Hours Spent')).issubset(self.worklogs[jiraID].keys()):
                    csvwriter.writerow([
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{jiraID}\"),\"{jiraID}\")',
                        self.worklogs[jiraID]['is production support'],
                        self.worklogs[jiraID]['description'],
                        self.worklogs[jiraID]['Hours Spent for the Month'],
                        self.worklogs[jiraID]['Total Hours Spent']])
                
        print(f"Writing to {self.fileName} done.")

