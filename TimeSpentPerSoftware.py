from WorkLogsForEachSW import WorkLogsForEachSW

# This class is responsible for querying each of the
# PROJECT items belonging to the various SW
class TimeSpentPerSoftware:
    def __init__(self, desiredMonth, desiredYear, listOfSW) -> None:
        self.software = {}
        self.listOfSW = listOfSW
        self.worklogsForEachSW = WorkLogsForEachSW(desiredMonth, desiredYear)

    def extractItemsPerSW(self, person, jIRAService):
        self.software[person] = {}
        for sw in self.listOfSW:
            self.software[person][sw] = jIRAService.queryJIRAPerSW(person, sw)

    def getTimeSpentForEachSW(self, person):
        return self.worklogsForEachSW.getWorkLogsForEachSW(self.software[person], person)
