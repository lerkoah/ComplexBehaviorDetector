'''
    Simple socket server using threads
'''

import socket
import threading





t = threading.Thread(target=clientthread)
w = threading.Thread(target=serverthread)
w.start()
t.start()