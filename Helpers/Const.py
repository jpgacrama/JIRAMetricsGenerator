# File containing constants
class Const:
    def __init__(self) -> None:
        self.credentialFile = None
        self.filenameForHoursSpentPerSW = 'HoursPerSW.csv'
        self.filenameForTimeSpentPerPerson = 'TimePerPerson.csv'
        self.filenameForFinishedItemsPerPerson = 'FinishedItems.csv'
        self.filenameForUnfinishedItemsPerPerson = 'UnfinishedItems.csv'
        self.filenameForAllItemsPerPerson = 'AllItems.csv'

    def setCredentialFile(self, fileName):
        self.credentialFile = fileName

    def setFilenameForHoursSpentPerSW(self, fileName):
        self.filenameForHoursSpentPerSW = fileName
        
    def setFilenameForTimeSpentPerPerson(self, fileName):
        self.filenameForTimeSpentPerPerson = fileName

    def setFilenameForFinishedItemsPerPerson(self, fileName):
        self.filenameForFinishedItemsPerPerson = fileName
        
    def setFilenameForUnfinishedItemsPerPerson(self, fileName):
        self.filenameForUnfinishedItemsPerPerson = fileName

    def setFilenameForAllItemsPerPerson(self, fileName):
        self.filenameForAllItemsPerPerson = fileName

    def get_JIRA_URL(self):
        return 'https://macrovue.atlassian.net'

    def getProject(self):
        return 'OMNI'

    def getCredentialFile(self):
        if not self.credentialFile:
            raise Exception('Credential File is not yet set.')
        else:
            return self.credentialFile

    def getStoryPointEstimate(self):
        return '\"Story point estimate\"'

    def getDoneStatuses(self):
        return "Done, \"READY FOR PROD RELEASE\""

    def getFilenameForHoursSpentPerSW(self):
        return self.filenameForHoursSpentPerSW

    def getFilenameForTimeSpentPerPerson(self):
        return self.filenameForTimeSpentPerPerson

    def getFilenameForFinishedItemsPerPerson(self):
        return self.filenameForFinishedItemsPerPerson
    
    def getFilenameForUnfinishedItemsPerPerson(self):
        return self.filenameForUnfinishedItemsPerPerson

    def getFilenameForAllItemsPerPerson(self):
        return self.filenameForAllItemsPerPerson

