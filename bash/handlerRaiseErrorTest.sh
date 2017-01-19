#! /bin/bash
#######################################################
## This script was make for run python scripts in monit
#######################################################
PYTHON_FILE=/home/lerko/Desktop/Detector/RaiseErrorTest.py
LOG_FILE=/home/lerko/Desktop/Detector/log/RaiseErrorTest.log

sudo python $PYTHON_FILE >> $LOG_FILE
