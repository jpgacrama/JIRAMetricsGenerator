#!/usr/bin/env python
import PySimpleGUI as sg

#set the theme for the screen/window
sg.theme('SystemDefault')
menu_def=['&File', ['&New File', '&Open...','Open &Module','---', '!&Recent Files','C&lose']],['&Save',['&Save File', 'Save &As','Save &Copy'  ]],['&Edit', ['&Cut', '&Copy', '&Paste']]
#define layout
layout=[[sg.Menu(menu_def, background_color='lightsteelblue',text_color='navy', disabled_text_color='yellow', font='Verdana', pad=(10,10))],
        [sg.Multiline(size=(80,10),tooltip='Write your Text here')],
        [sg.Text('File Name'),sg.Input(),sg.OptionMenu(values=['.txt','.pdf','.gif', '.jpg','.mp4','.gif','.dat','.sql'],size=(4,8),default_value='.doc',key='ftype')],
        [sg.Button('SAVE', font=('Times New Roman',12)),sg.Button('CANCEL', font=('Times New Roman',12))]]
#Define Window
win =sg.Window('Your Custom Editor',layout)
#Read  values entered by user
events,values=win.read()
#close first window
win.close()
