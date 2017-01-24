jenkinsPathConfig = '/etc/sysconfig/jenkins'
jenkinsPathConfigCopy = '/etc/sysconfig/jenkins.backup'

print '## Editing jenkins control file ##'
print 'Reading lines...',
with open(jenkinsPathConfig, 'r') as file:
    data = file.readlines()
print 'done.'

print 'Making the backup...',
with open(jenkinsPathConfigCopy, 'w') as file:
    file.writelines(data)
print 'done. [Backup is in %s]' % jenkinsPathConfigCopy
print 'Please, if you have any problem,\nreplace jenkins by jenkins.backup'

for i,line in enumerate(data):
    if 'JENKINS_USER="jenkins"\n' == line:
        print 'Line found'
        data[i] = 'JENKINS_USER="root"\n'
        break
print 'Rewriting jenkins control file...',
with open(jenkinsPathConfig, 'w') as file:
    file.writelines(data)
print 'done.'