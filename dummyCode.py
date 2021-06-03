#!/usr/bin/env python3

# NOTE: You cannot use this yet in Apple Silicon. But it's not really important for now

import matplotlib.pyplot as pyplot

# Generic plotter function
def plotData(dictionaryWorklog, person):
    if dictionaryWorklog == None or len(dictionaryWorklog) == 0 or person == None:
        print("You cannot plot data without any entries")
        exit(1)
    else:
        numerOfItems = len(dictionaryWorklog)
        pyplot.axis("equal")
        pyplot.pie([float(v) for v in dictionaryWorklog.values() if v != 0],
                   labels=[str(k)
                           for k, v in dictionaryWorklog.items() if v != 0],
                   autopct=lambda p: '{:.2f}%'.format(round(p, 2)) if p > 0 else '')
        pyplot.title(f"Hours distributon for person shown in percent")
        pyplot.tight_layout()
        pyplot.show()