# JIRAMetricsGenerator

Pre-requisites:
- Install matplotlib: python3 -m pip install matplotlib
  
  FOR APPLE SILICON:

    - python3 -m pip install Cython
    - Install numpy
        - $ git clone https://github.com/numpy/numpy.git
          $ cd numpy
          $ pip3 install . --no-binary :all: --no-use-pep517
  
    - Install matplotlib
        - git clone https://github.com/matplotlib/matplotlib.git

  
    Then you need to manually download qhull and extract the archive. (http://www.qhull.org/download/qhull-2020-src-8.0.2.tgz on Qhull Downloads) You will get a folder named qhull-2020.2. You then have to place the folder at matplotlib/build. The build folder may not exist so you might have to create it.

    Lastly, the following command will install the matplotlib on your M1 mac:

    $ cd matplotlib
    $ pip3 install . --no-binary :all:

Some items you may be interested in the future:
- value.fields.issuetype.description
- value.fields.worklog.worklogs[i].updateAuthor
- value.fields.worklog.worklogs[i].updated
