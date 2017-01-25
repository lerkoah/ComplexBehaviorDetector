import sys

def lineEditor(filePath, oldLine, newLine):
    print '##########################################################'
    print 'Starting to edit lines from %s' %filePath

    backupFile = filePath+'.backup'

    print 'Reading lines...',
    with open(filePath, 'r') as file:
        data = file.readlines()
    print 'done.'

    print 'Making the backup...',
    with open(backupFile, 'w') as file:
        file.writelines(data)
    print 'done. [Backup is in %s]' % backupFile
    print 'Please, if you have any problem, replace\n%s by %s' % (filePath, backupFile)

    for i, line in enumerate(data):
        if oldLine in line:
            print 'Line found'
            data[i] = data[i].replace(oldLine,newLine)
            print data[i]
            break
    print 'Rewriting file...',
    with open(filePath, 'w') as file:
        file.writelines(data)
    print 'done.'
    print '##########################################################'



if __name__ == '__main__':
    pathToEdit = sys.argv[1]
    oldLine = sys.argv[2]
    newLine = sys.argv[3]
    lineEditor(pathToEdit, oldLine, newLine)