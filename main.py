import socket
import thread
from emailSender import *

def sendEmailThread(receivedMessage):
    Message = receivedMessage.split(':::')
    print Message

    if len(Message) ==  3:
        # Email sender server information
        smtp = "smtp.gmail.com"
        smtpPort = 587
        fromAddr = "myadd"
        passw = "mypass"

        # Addres to send the email
        toAddr = "aheit.s.a@gmail.com"

        # Creating the sender
        sender = emailSender(smtp, smtpPort, fromAddr, passw)
        sender.connect()

        # Creating Massage body
        subject = Message[0]
        body = 'Detector Name: '+ Message[1] + '\nPriority: ' + Message[0] + "\nDescription:\n''\n" + Message[2] + "\n''"

        # Sending and disconnect
        sender.send(toAddr, subject, body)
        sender.disconnect()

def serverSocketMailer():
    HOST = ''  # Symbolic name meaning all available interfaces
    PORT = 8889  # Arbitrary non-privileged port

    # Creating sockets
    s = socket.socket()
    s.bind((HOST, PORT)) # binding...
    s.listen(1) # Listen only one client

    while True:
        print 'Waiting for a client...'
        sc, addr = s.accept() # Acepting client
        receivedMessage = sc.recv(1024) # Receiving data

        # Creating a thread for processing notification
        thread.start_new_thread(sendEmailThread,(receivedMessage, ))


    sender.disconnect()
    sc.close()
    s.close()
    return 1

def main():
    # myDetector = SilentTestDetector()
    # myDetector = AlertingTestDetector()
    # myDetector = HaltingTestDetector()
    # myDetector = RaiseErrorTestDetector()

    # detection = myDetector.execute()

    serverSocketMailer()

if __name__ == '__main__':
    main()
