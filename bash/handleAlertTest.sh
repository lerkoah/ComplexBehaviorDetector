#! /bin/bash
################################################################
## This file is used as a handler for run Alerting Test in Monit
################################################################
LOG_FILE=/home/lerko/Desktop/Detector/AlertingTest.log

sudo python /home/lerko/Desktop/Detector/AlertingTest.py >> $LOG_FILE
