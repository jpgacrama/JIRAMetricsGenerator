#!/usr/bin/env python3

from tkinter import SW
from dateutil.parser import parse
import os
import time
from numpy import size
import csv
import asyncio
import PySimpleGUI as sg
import json
import threading
from Helpers import TimeHelper, JIRAService, AutoVivification
from ReportGenerators import HoursSpentPerSW, AllItemsPerPerson

# JIRA-related information
URL = 'https://macrovue.atlassian.net'
CREDENTIAL_FILE = './data/Credentials.txt'
PROJECT = 'OMNI'
STORY_POINT_ESTIMATE = '\"Story point estimate\"'
ISSUE_TYPES = ['Project', 'Ad-hoc']
DONE_STATUSES = "Done, \"READY FOR PROD RELEASE\""

# Filenames for the output files
HOURS_SPENT_PER_SW = 'HoursPerSW.csv'
TIME_SPENT_PER_PERSON = 'TimePerPerson.csv'
FINISHED_ITEMS_PER_PERSON = 'FinishedItems.csv'
UNFINISHED_ITEMS_PER_PERSON = 'UnfinishedItems.csv'
ALL_ITEMS_PER_PERSON = 'AllItems.csv'

# DIRECTORY OF THE OUTPUT FOLDER
OUTPUT_FOLDER = './output/'

# Member and SW Information
with open('./data/members.json', 'r') as membersFile:
    MEMBERS = json.load(membersFile)

with open('./data/software.json', 'r') as softwareFile:
    SOFTWARE = json.load(softwareFile)

NUMBER_OF_PEOPLE = len(MEMBERS) # This is also the number of threads

# Multithreaded Class for ThreadDoneItemsPerPerson
class ThreadDoneItemsPerPerson(threading.Thread):
    def __init__(self, person, jiraService, itemsPerPerson):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.itemsPerPerson = itemsPerPerson

    def run(self):
        self.itemsPerPerson[self.person] = self.jiraService.queryNumberOfDoneItemsPerPerson(self.person)

class FinishedItemsPerPerson:
    def __init__(self, jiraService) -> None:
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.timeHelper = TimeHelper()
        self.itemsPerPerson = AutoVivification()
        self.worklogPerPerson = AutoVivification()
    
    def __extractFinishedItemsPerPerson__(self, progressBarFinishedItemsPerPerson):
        print("\n-------- GENERATING MATRIX OF FINISHED ITEMS PER PERSON --------\n")

        for person in MEMBERS:
            self.itemsPerPerson[person] = {}

        threads = [ThreadDoneItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in MEMBERS]

        for thread in threads:
            thread.start()

        i = 0
        for thread in threads:
            thread.join()
            i += 1
            progressBarFinishedItemsPerPerson.update_bar(i, NUMBER_OF_PEOPLE - 1)

        return self.itemsPerPerson

    def __computeFinishedItemsPerPerson__(self, logsPerValue, person, jiraID, description):
        if self.jiraIDKey != jiraID:
            self.worklogPerPerson[person][jiraID] = {}
            self.worklogPerPerson[person][jiraID]['description'] = description
            self.worklogPerPerson[person][jiraID]['Hours Spent for the Month'] = 0
            self.jiraIDKey = jiraID

        extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
        if extractedDateTime:
            timeSpent = logsPerValue.timeSpentSeconds
            timeSpent = self.timeHelper.convertToHours(timeSpent)
            self.worklogPerPerson[person][jiraID]['Hours Spent for the Month'] += timeSpent

    async def extractFinishedItemsPerPerson(self, progressBarFinishedItemsPerPerson):
        allWorklogs = self.__extractFinishedItemsPerPerson__(progressBarFinishedItemsPerPerson)
        for person in allWorklogs:
            for jiraID in allWorklogs[person]:                
                if not allWorklogs[person][jiraID]['Hours Spent for the Month']:
                    self.worklogPerPerson[person][jiraID] = {}
                    self.worklogPerPerson[person][jiraID]['description'] = allWorklogs[person][jiraID]['description']
                    self.worklogPerPerson[person][jiraID]['Hours Spent for the Month'] = 0
                
                for worklogPerJIRAId in allWorklogs[person][jiraID]['Hours Spent for the Month']:
                    description = allWorklogs[person][jiraID]['description']
                    self.__computeFinishedItemsPerPerson__(worklogPerJIRAId, person, jiraID, description)

        self.__generateCSVFile__()

    def __generateCSVFile__(self):
        fileName = FINISHED_ITEMS_PER_PERSON

        with open(fileName, 'w', newline='') as csv_file:
            csvwriter = csv.writer(csv_file, delimiter=',')
            
            # Initialize all columns
            csvwriter.writerow(['Name', 'JIRA ID', 'Description', 'Hours Spent for the Month'])   

            for person in self.worklogPerPerson:
                for jiraID in self.worklogPerPerson[person]:
                    csvwriter.writerow([
                        person,
                        f'=HYPERLINK(CONCAT("https://macrovue.atlassian.net/browse/", \"{jiraID}\"),\"{jiraID}\")',                        
                        self.worklogPerPerson[person][jiraID]['description'],
                        self.worklogPerPerson[person][jiraID]['Hours Spent for the Month']])
        
        print(f"Writing to {fileName} done.")

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
    def __init__(self, jiraService) -> None:
        self.jiraService = jiraService
        self.jiraIDKey = None
        self.timeHelper = TimeHelper()
        self.itemsPerPerson = AutoVivification()
        self.worklogPerPerson = AutoVivification()
    
    def __extractUnfinishedItemsPerPerson__(self, progressBarUnfinishedItemsPerPerson):
        print("\n-------- GENERATING MATRIX OF UNFINISHED ITEMS PER PERSON --------\n")

        for person in MEMBERS:
            self.itemsPerPerson[person] = {}

        threads = [ThreadUnfinishedItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in MEMBERS]

        for thread in threads:
            thread.start()

        i = 0
        for thread in threads:
            thread.join()
            i += 1
            progressBarUnfinishedItemsPerPerson.update_bar(i, NUMBER_OF_PEOPLE - 1)

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
        fileName = UNFINISHED_ITEMS_PER_PERSON
        
        with open(fileName, 'w', newline='') as csv_file:
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
        
        print(f"Writing to {fileName} done.")

# Multithreaded Class for ThreaditemsPerPerson
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
    def __init__(self, jiraService) -> None:
        self.jiraService = jiraService
        self.issueId = None
        self.issueTypeKey = None
        self.personKey = None
        self.timeHelper = TimeHelper()
        self.itemsPerPerson = AutoVivification()
        self.worklogPerPerson = AutoVivification()

    def __extractTimeSpentPerPerson__(self, progressBarTimeSpentPerPerson):
        print("\n-------- GENERATING MATRIX OF TIME SPENT PER PERSON --------\n")

        for person in MEMBERS:
            self.itemsPerPerson[person] = {}

        threads = [ThreadItemsPerPerson(
                person, self.jiraService, self.itemsPerPerson) for person in MEMBERS]

        for thread in threads:
            thread.start()

        i = 0
        for thread in threads:
            thread.join()
            i += 1
            progressBarTimeSpentPerPerson.update_bar(i, NUMBER_OF_PEOPLE - 1)
        
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
            if extractedDateTime.month == DESIRED_MONTH and extractedDateTime.year == DESIRED_YEAR:
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
        fileName = TIME_SPENT_PER_PERSON
        df.to_csv(fileName, index=True, header=MEMBERS.keys())
        print(f"Writing to {fileName} done.")

def generateReports(progressBarHoursPerSW,
               progressBarTimeSpentPerPerson,
               progressBarFinishedItemsPerPerson,
               progressBarUnfinishedItemsPerPerson,
               progressBarAllItemsPerPerson):
    jiraService = JIRAService.JIRAService(
        CREDENTIAL_FILE, URL, UPDATED_DATE, MEMBERS, PROJECT, DONE_STATUSES)

    matrixOfWorklogsPerSW = HoursSpentPerSW.HoursSpentPerSW(
        jiraService, progressBarHoursPerSW, DESIRED_MONTH, DESIRED_YEAR, SOFTWARE, MEMBERS, HOURS_SPENT_PER_SW, OUTPUT_FOLDER)
    # timeSpentPerPerson = TimeSpentPerPerson(jiraService)
    # doneItemsPerPerson = FinishedItemsPerPerson(jiraService)
    # unfinishedItemsPerPerson = UnfinishedItemsPerPerson(jiraService)
    allItemsPerPerson = AllItemsPerPerson.AllItemsPerPerson(
        jiraService, progressBarHoursPerSW, DESIRED_MONTH, DESIRED_YEAR, MEMBERS, ALL_ITEMS_PER_PERSON, OUTPUT_FOLDER)

    try:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(matrixOfWorklogsPerSW.extractHoursPerSW()),
            # loop.create_task(timeSpentPerPerson.extractTimeSpentPerPerson(progressBarTimeSpentPerPerson)),
            # loop.create_task(doneItemsPerPerson.extractFinishedItemsPerPerson(progressBarFinishedItemsPerPerson)),
            # loop.create_task(unfinishedItemsPerPerson.extractUnfinishedItemsPerPerson(progressBarUnfinishedItemsPerPerson)),
            # loop.create_task(allItemsPerPerson.extractAllItemsPerPerson(progressBarAllItemsPerPerson)),
        ]
        start = time.perf_counter()
        loop.run_until_complete(asyncio.wait(tasks))
    except Exception as e:
        print('There was a problem:')
        print(str(e))
    finally:
        loop.close()

    elapsedTimeInMinutes = (time.perf_counter() - start) / 60
    reportGeneratingTime = f'{round(elapsedTimeInMinutes, 2)}'
    return reportGeneratingTime

def name(name):
    nameSize = 60
    dots = nameSize-len(name)-2
    return sg.Text(name + ' ' + '•'*dots, size=(nameSize,1), justification='r',pad=(0,0), font='Courier 10')

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # START THE GUI
    sg.theme('Default1')

    global HOURS_SPENT_PER_SW, TIME_SPENT_PER_PERSON, FINISHED_ITEMS_PER_PERSON
    global UNFINISHED_ITEMS_PER_PERSON, ALL_ITEMS_PER_PERSON, CREDENTIAL_FILE

    try:
        layout =[
            [sg.Text('SELECT CREDENTIAL FILE')],
            [name('Credential File'),
                sg.InputText(key='fileForCredentials', size=(40,1), default_text=CREDENTIAL_FILE), 
                sg.FileBrowse(size=(15,1))],
            [sg.VerticalSeparator(pad=(0,0))],
            [sg.Text('SELECT DATE RANGE')],
            [name('Select Start Date'),
                sg.Input(key='start_date', size=(40,1), justification='center'), 
                sg.CalendarButton('Select Start Date', close_when_date_chosen=True, no_titlebar=False, format='%Y-%m-%d', size=(15,1))],
            [name('Select End Date'),
                sg.Input(key='end_date', size=(40,1), justification='center'),
                sg.CalendarButton('Select End Date', close_when_date_chosen=True, no_titlebar=False, format='%Y-%m-%d', size=(15,1))],
            [sg.VerticalSeparator(pad=(0,0))],
            [sg.Text('ENTER FILE NAMES FOR THE REPORTS IN CSV FORMAT')],
            [name('Hours Spent per SW'),
                sg.InputText(key='fileForHoursPerSW', size=(40,1), default_text=HOURS_SPENT_PER_SW), 
                sg.FileBrowse(size=(15,1))],
            [name('Time Spent Per Person'),
                sg.InputText(key='fileForTimeSpentPerPerson', size=(40,1), default_text=TIME_SPENT_PER_PERSON), 
                sg.FileBrowse(size=(15,1))],
            [name('Finished Items Per Person'),
                sg.InputText(key='fileForFinishedItemsPerPerson', size=(40,1), default_text=FINISHED_ITEMS_PER_PERSON), 
                sg.FileBrowse(size=(15,1))],
            [name('Unfinished Items Per Person'),
                sg.InputText(key='fileForUnfinishedItemsPerPerson', size=(40,1), default_text=UNFINISHED_ITEMS_PER_PERSON), 
                sg.FileBrowse(size=(15,1))],
            [name('All Items Per Person'),
                sg.InputText(key='fileForAllItemsPerPerson', size=(40,1), default_text=ALL_ITEMS_PER_PERSON), 
                sg.FileBrowse(size=(15,1))],
            [sg.VerticalSeparator(pad=(0,0))],
            [sg.Text('PROGRESS BARS')],
            [name('Hours Spent per SW'),
                sg.ProgressBar(1, orientation='h', size=(39.4, 20), key='progressHoursPerSW')],
            [name('Time Spent Per Person'),
                sg.ProgressBar(1, orientation='h', size=(39.4, 20), key='timeSpentPerPerson')],
            [name('Finished Items Per Person'),
                sg.ProgressBar(1, orientation='h', size=(39.4, 20), key='doneItemsPerPerson')],
            [name('Unfinished Items Per Person'),
                sg.ProgressBar(1, orientation='h', size=(39.4, 20), key='unfinishedItemsPerPerson')],
            [name('All Items Per Person. This takes time. Please be patient'),
                sg.ProgressBar(1, orientation='h', size=(39.4, 20), key='allItemsPerPerson')],
            [sg.Button('Start', size=(15,1)), sg.Exit(size=(15,1))],
            ]

        layout = [[sg.Column(layout, element_justification='c')]]

        window = sg.Window('JIRA Metrics Generator', layout).Finalize()
        progressBarHoursPerSW = window['progressHoursPerSW']
        progressBarTimeSpentPerPerson = window['timeSpentPerPerson']
        progressBarFinishedItemsPerPerson = window['doneItemsPerPerson']
        progressBarUnfinishedItemsPerPerson = window['unfinishedItemsPerPerson']
        progressBarAllItemsPerPerson = window['allItemsPerPerson']

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Exit':
                break
            elif event == 'Start':
                # File for Credentials
                fileForCredentials = values['fileForCredentials']
                if not fileForCredentials.endswith('txt'):
                    raise Exception('Filename should have .txt extension')
                else:
                    if fileForCredentials != CREDENTIAL_FILE:
                        CREDENTIAL_FILE = fileForCredentials

                # Start and End Dates
                startDate = values['start_date']
                endDate = values['end_date']
                global UPDATED_DATE
                UPDATED_DATE = f"worklogDate >= \"{startDate}\" AND worklogDate < \"{endDate}\""
                startDate = parse(startDate, fuzzy=True)
                endDate = parse(endDate, fuzzy=True)

                if endDate < startDate:
                    raise Exception('Start Date should be earlier than End Date')

                if startDate.year != endDate.year:
                    raise Exception('Start Year and End Year should be the same')
                else:
                    global DESIRED_YEAR
                    DESIRED_YEAR = endDate.year
                
                if endDate.month != startDate.month:
                    raise Exception('You should generate a report on the same month')
                else:
                    global DESIRED_MONTH
                    DESIRED_MONTH = endDate.month

                # Filenames for output files

                fileForHoursPerSW = values['fileForHoursPerSW']
                if not fileForHoursPerSW.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForHoursPerSW != HOURS_SPENT_PER_SW:
                        HOURS_SPENT_PER_SW = fileForHoursPerSW

                fileForTimeSpentPerPerson = values['fileForTimeSpentPerPerson']
                if not fileForTimeSpentPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForTimeSpentPerPerson != TIME_SPENT_PER_PERSON:
                        TIME_SPENT_PER_PERSON = fileForTimeSpentPerPerson

                fileForFinishedItemsPerPerson = values['fileForFinishedItemsPerPerson']
                if not fileForFinishedItemsPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForFinishedItemsPerPerson != FINISHED_ITEMS_PER_PERSON:
                        FINISHED_ITEMS_PER_PERSON = fileForFinishedItemsPerPerson

                fileForUnfinishedItemsPerPerson = values['fileForUnfinishedItemsPerPerson']
                if not fileForUnfinishedItemsPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForUnfinishedItemsPerPerson != UNFINISHED_ITEMS_PER_PERSON:
                        UNFINISHED_ITEMS_PER_PERSON = fileForUnfinishedItemsPerPerson

                fileForAllItemsPerPerson = values['fileForAllItemsPerPerson']
                if not fileForAllItemsPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForAllItemsPerPerson != ALL_ITEMS_PER_PERSON:
                        ALL_ITEMS_PER_PERSON = fileForAllItemsPerPerson
                
                # Generate Reports
                reportGeneratingTime = generateReports(progressBarHoursPerSW,
                           progressBarTimeSpentPerPerson,
                           progressBarFinishedItemsPerPerson,
                           progressBarUnfinishedItemsPerPerson,
                           progressBarAllItemsPerPerson)
                sg.popup(f'Finished generating all reports. It took {reportGeneratingTime} minutes 😄.', title='Success')
                break

    except Exception as error:
        sg.popup_error(error, title='Exception Raised')

    window.CloseNonBlocking()

if __name__ == "__main__":
    main()
