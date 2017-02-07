import socket

def serverSocketMailer():
    HOST = '10.195.60.145'  # Symbolic name meaning all available interfaces
    # HOST = ''
    PORT = 5959 # Arbitrary non-privileged port

    # Creating sockets
    s = socket.socket()
    s.bind((HOST, PORT)) # binding...
    s.listen(1) # Listen only one client

    while True:
        print 'Waiting for a client...'
        sc, addr = s.accept() # Acepting client
        receivedMessage = sc.recv(1024) # Receiving data

        # Creating a thread for processing notification
        print receivedMessage


    sender.disconnect()
    sc.close()
    s.close()
    return 1

def main():
    serverSocketMailer()

if __name__ == '__main__':
    main()