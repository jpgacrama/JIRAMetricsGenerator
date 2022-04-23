from Helpers import TimeHelper

class APersonsWorkLogsForEachSW:
    def __init__(self, desiredMonth, desiredYear) -> None:
        self.dictionaryWorklog = {}
        self.timeHelper = TimeHelper.TimeHelper()
        self.issueId = None
        self.totalTimeSpent = 0
        self.newTimeSpent = 0
        self.desiredMonth = desiredMonth
        self.desiredYear = desiredYear

    def __computeTotalTimeSpent__(self, value, person, sw):
        self.issueId = None
        self.totalTimeSpent = 0
        self.newTimeSpent = 0

        # logsPerValue means first log, second log, etc.
        for logsPerValue in value:
            extractedDateTime = self.timeHelper.trimDate(logsPerValue.started)
            if extractedDateTime:
                if extractedDateTime.month == self.desiredMonth and extractedDateTime.year == self.desiredYear:
                    if self.issueId != logsPerValue.issueId:
                        self.totalTimeSpent = 0
                        self.issueId = logsPerValue.issueId
                        self.totalTimeSpent = logsPerValue.timeSpentSeconds
                        self.totalTimeSpent = self.timeHelper.convertToHours(self.totalTimeSpent)
                        self.dictionaryWorklog[person][sw][self.issueId] = self.totalTimeSpent
                    else:
                        newTimeSpent = 0
                        newTimeSpent = logsPerValue.timeSpentSeconds
                        newTimeSpent = self.timeHelper.convertToHours(newTimeSpent)
                        self.totalTimeSpent += newTimeSpent
                        self.dictionaryWorklog[person][sw][self.issueId] = self.totalTimeSpent

    def getAPersonsWorkLogForEachSW(self, software, person):
        self.dictionaryWorklog[person] = {}
        if software:
            for sw in software:
                self.dictionaryWorklog[person][sw] = {}
                for value in software[sw].values():
                    self.__computeTotalTimeSpent__(value, person, sw)
                self.dictionaryWorklog[person][sw] = round(sum(self.dictionaryWorklog[person][sw].values()), 2)
            return self.dictionaryWorklog

        else:
            print("TimeSpentPerSoftware.extractItemsPerSW() should be run first.")
            exit()
