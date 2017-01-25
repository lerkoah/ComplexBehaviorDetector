# Complex Behavior Detector - ALMA Summer Job
This is the repository for the project Complex Behavior Detector from alma. This is the Lerko's Summer Job. In this repository I'm going to save the principal scripts and instructions for running the framework in your computer.

## Easy Install
We are working on CentOS 6.8 and Red Hat Entrerprise Linux 6.8. Then the following instruction are thinking for this contexts.

For install de framework you have to run the installJenkinsFramework.sh as root permissions. That's means go to install folder and execute:
```sh
./installJenkinsFramework.sh
```

## Detectors Classes

### Detectors Type 1
The principal file for this detectors is `DetectorType1.py`. Additionally, You can find tests for this Detectors that you can run in a Job Manager with the following syntax:

```sh
python -u /home/lerko/Desktop/ComplexBehaviorDetector/DetectorsType1.py DetectorName Priority
```

The argument ``Priority`` can be ommit. For example, if we want to execute Alerting Detector with Priority Alarm ``CRITICAL`` we must to execute:

```sh
python -u /home/lerko/Desktop/ComplexBehaviorDetector/DetectorsType1.py AlertingDetector CRITICAL
```

The possible alarms levels are:

* DEBUG
* INFO
* WARNING
* CRITICAL

### Detector Type 2

### Detector Type 3
