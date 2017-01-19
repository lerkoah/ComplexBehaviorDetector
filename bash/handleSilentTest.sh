#! /bin/bash
################################################################
## This file is used as a handler for run Alerting Test in Monit
################################################################
LOG_FILE=/home/lerko/Desktop/Detector/SilentTest.log

sudo python /home/lerko/Desktop/Detector/SilentTest.py >> $LOG_FILE
