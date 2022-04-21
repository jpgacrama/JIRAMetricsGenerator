# JIRAMetricsGenerator

Pre-requisites:
- Install matplotlib: python3 -m pip install matplotlib
- Install Panda: python3 -m pip install pandas
  
  FOR APPLE SILICON:
    - You can install all the dependencies using Anaconda
      and let your IDE use its version of python

THINGS TO REMEMBER:
1. Place your Credentials.txt file inside the data folder. This file contains your JIRA API key 
2. All *.csv outputs are placed in the "output" folder 

CUSTOM FIELDS:
- customfield_11428: SW
- customfield_11414: Component
- customfield_11410: Story Point
- self.jiraService.issue(str(issue)).raw['fields']['status']['name'] - for Checking current status