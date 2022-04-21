#!/usr/bin/env python3

from tkinter import SW
from dateutil.parser import parse
import os
import time
import asyncio
import PySimpleGUI as sg
import json
import shutil
from Helpers import JIRAService, Const
from ReportGenerators import HoursSpentPerSW, AllItemsPerPerson
from ReportGenerators import TimeSpentPerPerson, FinishedItemsPerPerson, UnfinishedItemsPerPerson


# DIRECTORY OF THE OUTPUT FOLDER
OUTPUT_FOLDER = './output/'

# Member and SW Information
with open('./data/members.json', 'r') as membersFile:
    MEMBERS = json.load(membersFile)

with open('./data/software.json', 'r') as softwareFile:
    SOFTWARE = json.load(softwareFile)

NUMBER_OF_PEOPLE = len(MEMBERS) # This is also the number of threads

def generateReports(
               const,
               progressBarHoursPerSW,
               progressBarTimeSpentPerPerson,
               progressBarFinishedItemsPerPerson,
               progressBarUnfinishedItemsPerPerson,
               progressBarAllItemsPerPerson):
    jiraService = JIRAService.JIRAService(
       const.getCredentialFile(), const.get_JIRA_URL(), UPDATED_DATE, MEMBERS, const.getProject(), const.getDoneStatuses())

    matrixOfWorklogsPerSW = HoursSpentPerSW.HoursSpentPerSW(
        jiraService, progressBarHoursPerSW, DESIRED_MONTH, DESIRED_YEAR, SOFTWARE, MEMBERS, const.getFilenameForHoursSpentPerSW(), OUTPUT_FOLDER)
    timeSpentPerPerson = TimeSpentPerPerson.TimeSpentPerPerson(
        jiraService, DESIRED_MONTH, DESIRED_YEAR, MEMBERS, const.getFilenameForTimeSpentPerPerson(),  OUTPUT_FOLDER)
    doneItemsPerPerson = FinishedItemsPerPerson.FinishedItemsPerPerson(jiraService, MEMBERS, const.getFilenameForFinishedItemsPerPerson(), OUTPUT_FOLDER)
    unfinishedItemsPerPerson = UnfinishedItemsPerPerson.UnfinishedItemsPerPerson(jiraService, MEMBERS, const.getFilenameForUnfinishedItemsPerPerson(), OUTPUT_FOLDER)
    allItemsPerPerson = AllItemsPerPerson.AllItemsPerPerson(
        jiraService, progressBarHoursPerSW, DESIRED_MONTH, DESIRED_YEAR, MEMBERS, const.getFilenameForAllItemsPerPerson(), OUTPUT_FOLDER)

    try:
        loop = asyncio.get_event_loop()
        tasks = [
            loop.create_task(matrixOfWorklogsPerSW.extractHoursPerSW()),
            loop.create_task(timeSpentPerPerson.extractTimeSpentPerPerson(progressBarTimeSpentPerPerson)),
            loop.create_task(doneItemsPerPerson.extractFinishedItemsPerPerson(progressBarFinishedItemsPerPerson)),
            loop.create_task(unfinishedItemsPerPerson.extractUnfinishedItemsPerPerson(progressBarUnfinishedItemsPerPerson)),
            loop.create_task(allItemsPerPerson.extractAllItemsPerPerson(progressBarAllItemsPerPerson)),
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

def clean():
    for folder, subfolders, files in os.walk('./'): 
        for file in files: 
            if file.endswith('.csv'): 
                path = os.path.join(folder, file) 
                    
                # printing the path of the file 
                # to be deleted 
                print('deleted : ', path )
                
                # deleting the csv file 
                os.remove(path)
    
    shutil.rmtree(OUTPUT_FOLDER, ignore_errors=True, onerror=None)
    os.system('cls' if os.name == 'nt' else 'clear')

def setConstants():
    const = Const.Const()
    const.setCredentialFile('./data/Credentials.txt')
    return const

def main():
    clean()
    const = setConstants()
    
    # START THE GUI
    sg.theme('Default1')

    try:
        layout =[
            [sg.Text('SELECT CREDENTIAL FILE')],
            [name('Credential File'),
                sg.InputText(key='fileForCredentials', size=(40,1), default_text=const.getCredentialFile()), 
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
                sg.InputText(key='fileForHoursPerSW', size=(40,1), default_text=const.getFilenameForHoursSpentPerSW()), 
                sg.FileBrowse(size=(15,1))],
            [name('Time Spent Per Person'),
                sg.InputText(key='fileForTimeSpentPerPerson', size=(40,1), default_text=const.getFilenameForTimeSpentPerPerson()), 
                sg.FileBrowse(size=(15,1))],
            [name('Finished Items Per Person'),
                sg.InputText(key='fileForFinishedItemsPerPerson', size=(40,1), default_text=const.getFilenameForFinishedItemsPerPerson()), 
                sg.FileBrowse(size=(15,1))],
            [name('Unfinished Items Per Person'),
                sg.InputText(key='fileForUnfinishedItemsPerPerson', size=(40,1), default_text=const.getFilenameForUnfinishedItemsPerPerson()), 
                sg.FileBrowse(size=(15,1))],
            [name('All Items Per Person'),
                sg.InputText(key='fileForAllItemsPerPerson', size=(40,1), default_text=const.getFilenameForAllItemsPerPerson()), 
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
                    if fileForCredentials != const.getCredentialFile():
                        const.setCredentialFile(fileForCredentials)

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
                    if fileForHoursPerSW != const.getFilenameForHoursSpentPerSW():
                        const.setFilenameForHoursSpentPerSW(fileForHoursPerSW)

                fileForTimeSpentPerPerson = values['fileForTimeSpentPerPerson']
                if not fileForTimeSpentPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForTimeSpentPerPerson != const.getFilenameForTimeSpentPerPerson():
                        const.setFilenameForTimeSpentPerPerson(fileForTimeSpentPerPerson)

                fileForFinishedItemsPerPerson = values['fileForFinishedItemsPerPerson']
                if not fileForFinishedItemsPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForFinishedItemsPerPerson != const.getFilenameForFinishedItemsPerPerson():
                        const.setFilenameForFinishedItemsPerPerson(fileForFinishedItemsPerPerson)

                fileForUnfinishedItemsPerPerson = values['fileForUnfinishedItemsPerPerson']
                if not fileForUnfinishedItemsPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForUnfinishedItemsPerPerson != const.getFilenameForUnfinishedItemsPerPerson():
                        const.setFilenameForUnfinishedItemsPerPerson(fileForUnfinishedItemsPerPerson)

                fileForAllItemsPerPerson = values['fileForAllItemsPerPerson']
                if not fileForAllItemsPerPerson.endswith('csv'):
                    raise Exception('Filename should have .csv extension')
                else:
                    if fileForAllItemsPerPerson != const.getFilenameForAllItemsPerPerson():
                        const.setFilenameForAllItemsPerPerson(fileForAllItemsPerPerson)
                
                # Generate Reports
                reportGeneratingTime = generateReports(
                           const,
                           progressBarHoursPerSW,
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
