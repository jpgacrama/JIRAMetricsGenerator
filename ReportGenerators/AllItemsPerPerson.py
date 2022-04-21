import threading
import csv
from Helpers import TimeHelper, AutoVivification

class ThreadAllItemsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, itemsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.itemsPerPerson = itemsPerPerson

    def run(self):
        self.itemsPerPerson[self.person] = self.jiraService.queryAllItemsPerPerson(self.person)

class AllItemsPerPerson:
    def __init__(self,
            jiraService,
            progressBarHoursPerSW,
            desiredMonth,
            desiredYear,
            members,
            fileName) -> None:
        self.jiraService = jiraService
        self.progressBarHoursPerSW = progressBarHoursPerSW
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear
        self.members = members
        self.fileName = fileName
        self.jiraIDKey = None
        self.personKey = None
        self.timeHelper = TimeHelper.TimeHelper()
        self.itemsPerPerson = AutoVivification.AutoVivification()
        self.worklogPerPerson = AutoVivification.AutoVivification()
    
    def __extractAllItemsPerPerson__(self, progressBarAllItemsPerPerson):
        print("\n-------- GENERATING MATRIX OF ALL ITEMS PER PERSON --------\n")
        
        for person in self.members:
            self.itemsPerPerson[person] = {}

        threads = [ThreadAllItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in self.members]

        for thread in threads:
            thread.start()

        i = 0
        numberOfPeople = len(self.members)
        for thread in threads:
            thread.join()
            i += 1
            progressBarAllItemsPerPerson.update_bar(i, numberOfPeople - 1)
        
        return self.itemsPerPerson

    def __computeAllItemsPerPerson__(
        self, logsPerValue, person, jiraID, description, software,
        component, issueType, storyPoint, status, dateStarted, dateFinished):
        
        if self.personKey != person:
            self.worklogPerPerson[person] = {}
            self.personKey = person

        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[person][jiraID] = {}
            self.worklogPerPerson[person][jiraID]['description'] = description
            self.worklogPerPerson[person][jiraID]['Software'] = software
            self.worklogPerPerson[person][jiraID]['Component'] = component
            self.worklogPerPerson[person][jiraID]['Issue Type'] = issueType
            self.worklogPerPerson[person][jiraID]['Story Point'] = storyPoint
            self.worklogPerPerson[person][jiraID]['Status'] = status
            self.worklogPerPerson[person][jiraID]['Date Started'] = dateStarted
            self.worklogPerPerson[person][jiraID]['Date Finished'] = dateFinished
            self.worklogPerPerson[person][jiraID]['Hours Spent for the Month'] = 0
            self.worklogPerPerson[person][jiraID]['Total Hours Spent'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            
            # For Hours Spent for the Current Month
            if extractedDateTime.month == self.desiredMonth and extractedDateTime.year == self.desiredYear:
                timeSpent = logsPerValue.timeSpentSeconds
                timeSpent = self.timeHelper.convertToHours(timeSpent)
                self.worklogPerPerson[person][jiraID]['Hours Spent for the Month'] += timeSpent
            
            # For Total Hours Spent
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerPerson[person][jiraID]['Total Hours Spent'] += timeSpent

    async def extractAllItemsPerPerson(self, progressBarAllItemsPerPerson):
        allWorklogs = self.__extractAllItemsPerPerson__(progressBarAllItemsPerPerson)
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:
                for worklogPerJIRAId in allWorklogs[person][jiraID]['Hours Spent for the Month']:
                    description = allWorklogs[person][jiraID]['description']
                    software = allWorklogs[person][jiraID]['Software']
                    component = allWorklogs[person][jiraID]['Component']
                    issueType = allWorklogs[person][jiraID]['Issue Type']
                    storyPoint = allWorklogs[person][jiraID]['Story Point']
                    status = allWorklogs[person][jiraID]['Status']
                    dateStarted = allWorklogs[person][jiraID]['Date Started']
                    dateFinished = allWorklogs[person][jiraID]['Date Finished']
                    
                    self.__computeAllItemsPerPerson__(
                        worklogPerJIRAId, person, jiraID,
                        description, software, component, issueType,
                        storyPoint, status, dateStarted, dateFinished)

        self.__generateCSVFile__()

    def __generateCSVFile__(self):
        with open(self.fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['Name', 'JIRA ID', 'Description',
                'Software', 'Component', 'Issue Type', 'Story Point',
                'Status', 'Date Started', 'Date Finished',
                'Hours Spent for the Month', 'Total Hours Spent'])

            for person in self.worklogPerPerson:
                for jiraID in self.worklogPerPerson[person]:
                    csvwriter.writerow([
                        person, 
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{jiraID}\"),\"{jiraID}\")',
                        self.worklogPerPerson[person][jiraID]['description'],
                        self.worklogPerPerson[person][jiraID]['Software'],
                        self.worklogPerPerson[person][jiraID]['Component'],
                        self.worklogPerPerson[person][jiraID]['Issue Type'],
                        self.worklogPerPerson[person][jiraID]['Story Point'],
                        self.worklogPerPerson[person][jiraID]['Status'],
                        self.worklogPerPerson[person][jiraID]['Date Started'],
                        self.worklogPerPerson[person][jiraID]['Date Finished'],
                        self.worklogPerPerson[person][jiraID]['Hours Spent for the Month'],
                        self.worklogPerPerson[person][jiraID]['Total Hours Spent']])
        
        print(f"Writing to {self.fileName} done.")
