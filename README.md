# JIRAMetricsGenerator

Pre-requisites:
- Install matplotlib: python3 -m pip install matplotlib
- Install Panda: python3 -m pip install pandas
  
  FOR APPLE SILICON:

    To install matplotlib

    - python3 -m pip install cython   
    - python3 -m pip install --no-binary :all: --no-use-pep517 numpy
    - brew install libjpeg
    - python3 -m pip install matplotlib

    To install pandas
    - pip3 install Cython
    - git clone https://github.com/numpy/numpy.git 
    - cd numpy
    - pip3 install . --no-binary :all: --no-use-pep517

Some items you may be interested in the future:
- value.fields.issuetype.description
- value.fields.worklog.worklogs[i].updateAuthor
- value.fields.worklog.worklogs[i].updated
