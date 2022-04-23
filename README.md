# JIRA Metrics Generator for HALO Project

This creates various CSV reports which are needed for [HALO](https://www.halo-technologies.com/company)

## Pre-requisites:

- Install [Anaconda](https://www.google.com/search?q=anaconda)
- On your command line (or Terminal in Unix-based systems), type: 
-- conda env create -f environment.yml or 
-- conda env create -f windows_environment.yml (for Windows OS)

## Things to Remember:
1. Place your *Credentials.txt* file inside the data folder. This file contains your JIRA API key 
2. All *.csv outputs are placed in the *output* folder 

## Meaning of Custom Fields which are used in this SW:
- customfield_11428: SW
- customfield_11414: Component
- customfield_11410: Story Point
- self.jiraService.issue(str(issue)).raw['fields']['status']['name'] - for Checking current status

## For Questions
- Reach out to Jonas Gacrama(jonas.gacrama@flexisourceitph.com) if you have any problems running this SW. 😃