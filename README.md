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

THINGS TO REMEMBER:
1. Use JIRA query to find out the actual value for the current OMNI Sprint
   and place its corresponding number under the SPRINT Global Variable
