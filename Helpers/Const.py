# File containing constants
class Const:
    def __init__(self) -> None:
        self.credentialFile = None

    def setCredentialFile(self, fileName):
        self.credentialFile = fileName
        
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