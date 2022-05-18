from jira import JIRA

class JIRAService:
    def __init__(self, 
                 CredentialsFile,
                 URL,
                 worklogDate,
                 updatedDate,
                 members,
                 project,
                 doneStatuses) -> None:
        self.username = None
        self.api_token = None
        self.CredentialsFile = CredentialsFile
        self.URL = URL
        self.worklogDate = worklogDate
        self.updatedDate = updatedDate
        self.members = members
        self.project = project
        self.doneStatuses = doneStatuses
        self.__logInToJIRA__()

    def __logInToJIRA__(self):
        with open(self.CredentialsFile, 'r', newline='') as file:
            lines = file.read().splitlines() 

        username = lines[0]
        api_token = lines[1]
        self.jiraService = JIRA(self.URL, basic_auth=(username, api_token))
        pass

    def queryEpics(self, progressBar):
        allEpics = self.jiraService.search_issues(
            f"""
                {self.updatedDate}
                AND project = {self.project}
                AND issuetype = Epic
             """,
            fields="worklog")

        allWorklogs = {}
        numberOfEpics = len(allEpics)
        i = 0
        
        for issue in allEpics:
            allWorklogs[str(issue)] = {} 
            allWorklogs[str(issue)]['description'] = {}
            allWorklogs[str(issue)]['is production support'] = {}

            allWorklogs[str(issue)]['is production support'] = True if self.jiraService.issue(str(issue)).raw['fields']['labels'] == ['production-support'] else False
            allWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            children = self.jiraService.search_issues(f"parent={str(issue)}")
            
            for child in children:
                allWorklogs[str(issue)][str(child)] = {}
                allWorklogs[str(issue)][str(child)]['description'] = {}
                allWorklogs[str(issue)][str(child)]['description'] = self.jiraService.issue(str(child)).fields.summary
                allWorklogs[str(issue)][str(child)]['Hours Spent for the Month'] = self.jiraService.worklogs(child)
                allWorklogs[str(issue)][str(child)]['Total Hours Spent'] = self.jiraService.worklogs(child)
            
            i += 1
            progressBar.update_bar(i, numberOfEpics - 1)

        # Returns a list of Worklogs
        return allWorklogs

    def queryNumberOfDoneItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f"""
                {self.worklogDate}
                AND assignee in ({self.members[person]})
                AND project = {self.project}
                AND status in ({self.doneStatuses})
             """,
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = {}
            allWorklogs[str(issue)]['description'] = {}
            allWorklogs[str(issue)]['Hours Spent for the Month'] = {}
            allWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            allWorklogs[str(issue)]['Hours Spent for the Month'] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

    def queryNumberOfUnfinishedItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f"""
                {self.worklogDate}
                AND assignee in ({self.members[person]})
                AND project = {self.project}
                AND NOT status in ({self.doneStatuses})
             """,
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = {}
            allWorklogs[str(issue)]['description'] = {}
            allWorklogs[str(issue)]['Total Hours Spent'] = {}
            allWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            allWorklogs[str(issue)]['Total Hours Spent'] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs
    
    # TODO: Removed Austin-specific query when this is successful
    def queryAllOperationalTicketsNotUnderAnEpic(self, progressBar):
        allIssues = self.jiraService.search_issues(
            f"""
                {self.worklogDate}
                AND project = {self.project}
                AND parent is empty
                AND assignee in (5fbb3d037cc1030069500950) 
             """,
            fields="worklog")

        allOperationalWorklogs = {}
        numberOfOperationalItems = len(allIssues)
        i = 0
        for issue in allIssues:
            allOperationalWorklogs[str(issue)] = {}
            allOperationalWorklogs[str(issue)]['is production support'] = {}
            allOperationalWorklogs[str(issue)]['description'] = {}
            allOperationalWorklogs[str(issue)]['Hours Spent for the Month'] = {}
            allOperationalWorklogs[str(issue)]['Total Hours Spent'] = {}

            allOperationalWorklogs[str(issue)]['is production support'] = True if self.jiraService.issue(str(issue)).raw['fields']['labels'] == ['production-support'] else False
            allOperationalWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            allOperationalWorklogs[str(issue)]['Hours Spent for the Month'] = self.jiraService.worklogs(issue)
            allOperationalWorklogs[str(issue)]['Total Hours Spent'] = self.jiraService.worklogs(issue)

            i += 1
            progressBar.update_bar(i, numberOfOperationalItems - 1)

        # Returns a list of Worklogs
        return allOperationalWorklogs
    
    def queryAllItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f"""
                {self.worklogDate}
                AND assignee in ({self.members[person]})
                AND project = {self.project}
             """,
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = {}
            allWorklogs[str(issue)]['description'] = {}
            allWorklogs[str(issue)]['Software'] = {}
            allWorklogs[str(issue)]['Component'] = {}
            allWorklogs[str(issue)]['Issue Type'] = {}
            allWorklogs[str(issue)]['Story Point'] = {}
            allWorklogs[str(issue)]['Status'] = {}
            allWorklogs[str(issue)]['Date Started'] = {}
            allWorklogs[str(issue)]['Date Finished'] = {}
            allWorklogs[str(issue)]['Hours Spent for the Month'] = {}
            allWorklogs[str(issue)]['Total Hours Spent'] = {}
            
            allWorklogs[str(issue)]['description'] = self.jiraService.issue(str(issue)).fields.summary
            allWorklogs[str(issue)]['Hours Spent for the Month'] = self.jiraService.worklogs(issue)
            allWorklogs[str(issue)]['Total Hours Spent'] = self.jiraService.worklogs(issue)

            if 'customfield_11428' in self.jiraService.issue(str(issue)).raw['fields'] and self.jiraService.issue(str(issue)).raw['fields']['customfield_11428']:
                allWorklogs[str(issue)]['Software'] = self.jiraService.issue(str(issue)).raw['fields']['customfield_11428']['value']

            if 'customfield_11414' in self.jiraService.issue(str(issue)).raw['fields'] and self.jiraService.issue(str(issue)).raw['fields']['customfield_11414']:
                allWorklogs[str(issue)]['Component'] = self.jiraService.issue(str(issue)).raw['fields']['customfield_11414']['value']
            
            allWorklogs[str(issue)]['Issue Type'] = self.jiraService.issue(str(issue)).raw['fields']['issuetype']['name']
            allWorklogs[str(issue)]['Story Point'] = self.jiraService.issue(str(issue)).raw['fields']['customfield_11410']
            allWorklogs[str(issue)]['Status'] = self.jiraService.issue(str(issue)).raw['fields']['status']['name']

            if self.jiraService.issue(str(issue)).raw['fields']['status']['name'] == 'Done':
                allWorklogs[str(issue)]['Date Finished'] = self.jiraService.issue(str(issue)).raw['fields']['statuscategorychangedate'][:10]

            if len(self.jiraService.issue(str(issue)).raw['fields']['worklog']['worklogs']) > 0:
                allWorklogs[str(issue)]['Date Started'] = self.jiraService.issue(str(issue)).raw['fields']['worklog']['worklogs'][0]['started'][:10]
            
        # Returns a list of Worklogs
        return allWorklogs

    def queryAdhocItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f'{self.worklogDate} AND assignee in ({self.members[person]}) AND project = {self.project} AND issuetype = Ad-hoc',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs
    
    def queryProjectItemsPerPerson(self, person):
        allIssues = self.jiraService.search_issues(
            f'{self.worklogDate} AND assignee in ({self.members[person]}) AND project = {self.project} AND issuetype != Ad-hoc',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs

    def queryJIRAPerSW(self, memberToQuery, swToQuery):
        allIssues = self.jiraService.search_issues(
            f'{self.worklogDate} AND assignee in ({self.members[memberToQuery]}) AND project = {self.project} AND "Software[Dropdown]" = \"{swToQuery}\"',
            fields="worklog")

        allWorklogs = {}
        for issue in allIssues:
            allWorklogs[str(issue)] = self.jiraService.worklogs(issue)

        # Returns a list of Worklogs
        return allWorklogs
