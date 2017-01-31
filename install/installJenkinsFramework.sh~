#! /bin/bash
MAIN_FILE=$(dirname $PWD)
PYTHON_FILE_DETECTOR_TEST=$MAIN_FILE"/DetectorsType1.py"
PYTHON_FILE_ALARMLISTENER=$MAIN_FILE"/log/JobAlarmListener.py"

if [[ "${PWD}" != *"install" ]]; then
	printf '\nPlease, go to ComplexBehaviorDetector/install for execute this script.\n';
	exit 1;
fi

echo '## Getting Jenkins repositories'
wget -O /etc/yum.repos.d/jenkins.repo https://pkg.jenkins.io/redhat-stable/jenkins.repo
rpm --import https://pkg.jenkins.io/redhat-stable/jenkins.io.key

yum install java
yum install jenkins

python lineEditorHandler.py /etc/sysconfig/jenkins JENKINS_USER="jenkins"\n JENKINS_USER="root"\n

echo -n 'Changing propietaries...';
chown -R root:root /var/lib/jenkins;
chown -R root:root /var/cache/jenkins;
chown -R root:root /var/log/jenkins;
echo 'done.';

echo -n "Host (e.g., localhost) > ";
read JENKINS_HOST;

echo "Setting Host..."
python lineEditorHandler.py /etc/sysconfig/jenkins 'JENKINS_LISTEN_ADDRESS=""' 'JENKINS_LISTEN_ADDRESS="'$JENKINS_HOST'"'

service jenkins start

echo "##########################################################"
echo "Please, go to jenkins, set your jenkins user and password."
echo "After default configuration, enter your jenkins user and"
echo "password here, we need them for the plugins configuration"
echo "##########################################################"

echo -n "Host (e.g., localhost) >";
read JENKINS_HOST;
echo -n "User > ";
read JENKINS_USER;
echo -n "Pass > ";
read -s JENKINS_PASS;


echo '## Installing Jenkins Plugins'
for req in $(cat requirements.txt);
do java -jar jenkins-cli.jar -s http://$JENKINS_HOST:8080/ install-plugin $req --username $JENKINS_USER --password $JENKINS_PASS;
done

cp -a jobs/* /var/lib/jenkins/jobs
cd /var/lib/jenkins/jobs

python $MAIN_FILE/install/lineEditorHandler.py /var/lib/jenkins/jobs/AlertingTest/config.xml "python -u /home/lerko/Desktop/ComplexBehaviorDetector/DetectorsType1.py AlertingDetector CRITICAL" "python $PYTHON_FILE_DETECTOR_TEST AlertingDetector CRITICAL"
python $MAIN_FILE/install/lineEditorHandler.py /var/lib/jenkins/jobs/HaltingTest/config.xml "python -u /home/lerko/Desktop/ComplexBehaviorDetector/DetectorsType1.py HaltingDetector" "python $PYTHON_FILE_DETECTOR_TEST HaltingDetector"
python $MAIN_FILE/install/lineEditorHandler.py /var/lib/jenkins/jobs/RaiseErrorTest/config.xml "python -u /home/lerko/Desktop/ComplexBehaviorDetector/DetectorsType1.py RaiseErrorDetector" "python $PYTHON_FILE_DETECTOR_TEST RaiseErrorDetector"
python $MAIN_FILE/install/lineEditorHandler.py /var/lib/jenkins/jobs/SilentTest/config.xml "python -u /home/lerko/Desktop/ComplexBehaviorDetector/DetectorsType1.py SilentDetector" "python $PYTHON_FILE_DETECTOR_TEST SilentDetector"

python $MAIN_FILE/install/lineEditorHandler.py /var/lib/jenkins/jobs/AlarmListener/config.xml "python /home/lerko/Desktop/ComplexBehaviorDetector/log/JobAlarmListener.py" "python $MAIN_FILE/log/JobAlarmListener.py"

cp $MAIN_FILE/install/org.jenkinsci.plugins.emailext_template.ExtendedEmailTemplatePublisher.xml /var/lib/jenkins/

exit 0
