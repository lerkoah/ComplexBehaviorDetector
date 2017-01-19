#! /bin/bash
#######################################################
## This script was make for run python scripts in monit
#######################################################
PYTHON_FILE=/home/lerko/Desktop/Detector/HaltingTest.py
LOG_FILE=/home/lerko/Desktop/Detector/log/HaltingTest.log

sudo python $PYTHON_FILE >> $LOG_FILE
