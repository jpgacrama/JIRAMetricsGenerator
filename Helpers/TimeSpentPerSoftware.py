from Helpers import APersonsWorkLogsForEachSW

class TimeSpentPerSoftware:
    def __init__(self, desiredMonth, desiredYear, listOfSW) -> None:
        self.software = {}
        self.listOfSW = listOfSW
        self.worklogsForEachSW = APersonsWorkLogsForEachSW.APersonsWorkLogsForEachSW(desiredMonth, desiredYear)

    def extractItemsPerSW(self, person, jIRAService):
        self.software[person] = {}
        for sw in self.listOfSW:
            self.software[person][sw] = jIRAService.queryJIRAPerSW(person, sw)

    def getTimeSpentForEachSW(self, person):
        return self.worklogsForEachSW.getAPersonsWorkLogForEachSW(self.software[person], person)
