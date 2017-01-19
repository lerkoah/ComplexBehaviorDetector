import socket

def serverSocket():
    HOST = ''  # Symbolic name meaning all available interfaces
    PORT = 8888  # Arbitrary non-privileged port

    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))

    s.listen(1)

    sc, addr = s.accept()

    receivedMessage = sc.recv(1024)
    Message = receivedMessage.split(':::')
    print Message[0]+'\n'+Message[1]

    sc.close()
    s.close()
    return 1

def main():
    serverSocket()

if __name__ == '__main__':
    main()