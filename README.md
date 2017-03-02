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

* INFO
* WARNING
* CRITICAL

### *Finite State Machine* Detector

These detectors have based on *Finite State Machines* (FSM), that means, we have to model the problem as FSM, and this is an input for the Detector. We define the model of the process using the library ProcessModel. For creating new machines you have to define the *symbols* and the *states*. A *symbol* is a simplification of a log for making it tratable. A *state* is defined by the *state name* and the *transitions*. We can defined ```AND``` transitions if we have no sequential transitions, i.e. the logs have the same timestamp.
