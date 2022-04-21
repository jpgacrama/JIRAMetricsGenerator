import pandas as pd
import threading
from Helpers import TimeSpentPerSoftware

# Multithreaded Class for MatrixOfWorklogsPerSW
class ThreadHoursSpentPerSW(threading.Thread):
    def __init__(self, person, jiraService, worklog, timeSpentPerSoftware):
        threading.Thread.__init__(self)
        self.person = person
        self.jiraService = jiraService
        self.worklog = worklog
        self.timeSpentPerSoftware = timeSpentPerSoftware

    def run(self):
        self.timeSpentPerSoftware.extractItemsPerSW(self.person, self.jiraService)
        self.worklog[self.person] = self.timeSpentPerSoftware.getTimeSpentForEachSW(self.person)

# This will be the "Caller" class
class HoursSpentPerSW:
    def __init__(self, 
            jiraService,
            progressBarHoursPerSW,
            desiredMonth,
            desiredYear,
            listOfSoftware,
            members,
            fileName) -> None:
        self.jiraService = jiraService
        self.progressBarHoursPerSW = progressBarHoursPerSW
        self.result = []
        self.worklog = {}
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear
        self.listOfSoftware = listOfSoftware
        self.members = members
        self.fileName = fileName

    # Function to get the total hours spent for every SW
    def __getTotal__(self):
        if len(self.result) == 0:
            print("You need to call MatrixOfWorklogsPerSW.generateMatrix() first")
            exit(1)
        else:
            df = pd.DataFrame(self.result[1:])
            df.loc['Column_Total'] = df.sum(numeric_only=True, axis=0)
            df.loc[:, 'Row_Total'] = df.sum(numeric_only=True, axis=1)
            self.result[1:] = df.values.tolist()

    async def extractHoursPerSW(self):
        timeSpentPerSoftware = TimeSpentPerSoftware.TimeSpentPerSoftware(
            self.desiredMonth, self.desiredYear, self.listOfSoftware)

        print("\n-------- GENERATING MATRIX OF TIME SPENT PER SW --------\n")

        for person in self.members:
            self.worklog[person] = {}

        threads = [ThreadHoursSpentPerSW(
                person, self.jiraService, self.worklog, timeSpentPerSoftware) for person in self.members]

        for thread in threads:
            thread.start()

        i = 0
        numberOfPeople = len(self.members)
        for thread in threads:
            thread.join()
            i += 1
            self.progressBarHoursPerSW.update_bar(i, numberOfPeople - 1)

        self.__cleanWorklogs__()
        self.__writeToCSVFile__()

    def __cleanWorklogs__(self):
        tempWorklog = {}
        for person in self.members:
            tempWorklog[person] = self.worklog[person][person]

        # Formatting the data before writing to CSV
        tempData = list(tempWorklog.values())
        subset = set()
        for element in tempData:
            for index in element:
                subset.add(index)
        tempResult = []
        tempResult.append(subset)
        for key, value in tempWorklog.items():
            tempData2 = []
            for index in subset:
                tempData2.append(value.get(index, 0))
            tempResult.append(tempData2)

        self.result = [[index for index, value in tempWorklog.items()]] + \
            list(map(list, zip(*tempResult)))

    def __writeToCSVFile__(self):
        if len(self.result) != 0:
            self.__getTotal__()
            self.result[0].insert(0, 'SW Names')

            # Putting "Total" at the last column
            self.result[0].insert(len(self.members) + 1, 'Total')

            # Putting "Total" at the last row
            self.result[-1].insert(0, 'Total')
            self.result[-1].pop(1)
            
            df = pd.DataFrame(self.result)
            df.to_csv(self.fileName, index=False, header=False)
        else:
            print("Data to write to CSV file is not yet available")
            exit(1)
        
        print(f'Writing to {self.fileName} done.')
