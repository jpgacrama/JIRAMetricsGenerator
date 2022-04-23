# TABLE OF CONTENTS
- [TABLE OF CONTENTS](#table-of-contents)
- [1. Introduction](#1-introduction)
  - [1.1. Pre-requisites](#11-pre-requisites)
  - [1.2. Things to Remember](#12-things-to-remember)
  - [1.3. Meaning of Custom Fields which are used in this SW](#13-meaning-of-custom-fields-which-are-used-in-this-sw)
  - [1.4. For Questions](#14-for-questions)

# 1. Introduction

This creates various CSV reports which are needed for [HALO](https://www.halo-technologies.com/company).
This assumes that all data are stored in [JIRA](https://macrovue.atlassian.net/jira/software/projects/OMNI/boards/17)
## 1.1. Pre-requisites

- Install [Anaconda](https://www.google.com/search?q=anaconda)
- On your command line (or Terminal in Unix-based systems), type: 
  - conda env create -f environment.yml or 
  - conda env create -f windows_environment.yml (for Windows OS)

## 1.2. Things to Remember
1. Place your *Credentials.txt* file inside the data folder. This file contains your JIRA API key 
2. All *.csv outputs are placed in the *output* folder 

## 1.3. Meaning of Custom Fields which are used in this SW
- customfield_11428: SW
- customfield_11414: Component
- customfield_11410: Story Point
- self.jiraService.issue(str(issue)).raw['fields']['status']['name'] - for Checking current status

## 1.4. For Questions
- Reach out to Jonas Gacrama(jonas.gacrama@flexisourceitph.com) if you have any problems running this SW. 😃