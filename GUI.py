#!/usr/bin/env python
import PySimpleGUI as sg

sg.theme('Default1')

# Getting Start Date and End Dates

layout = [[sg.Text('Choose your date range', key='-TXT-')],
      [sg.Input(key='start_date', size=(20,1)), sg.CalendarButton(
            'Select Start Date', close_when_date_chosen=True, location=(0,0), no_titlebar=False, format='%Y-%m-%d', )],
      [sg.Input(key='end_date', size=(20,1)), sg.CalendarButton(
            'Select End Date', close_when_date_chosen=True, location=(0,0), no_titlebar=False, format='%Y-%m-%d', )],
      [sg.Button('Read'), sg.Exit()]]

window = sg.Window('JIRA Metrics Generator', layout)

while True:
    event, values = window.read()
    print(event, values)
    if event == sg.WIN_CLOSED or event == 'Exit':
        break
    elif event == 'Read':
        startDate = values['start_date']
        endDate = values['end_date']

        print(f'Start Date: {startDate}')
        print(f'End Date: {endDate}')
window.close()