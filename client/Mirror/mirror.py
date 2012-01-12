from scratch import *
import threading
import socket
import json

SHOST = raw_input('Host IP: ')
SPORT = int( raw_input('Host Port: ') )

if not SHOST:
    print('You must enter a host.')
    exit(1)

if not SPORT:
    print('You must enter a port.')
    exit(1)

class Client(threading.Thread):
    
    def __init__(self):
        threading.Thread.__init__(self)
        try:
            self.s = Scratch()
        except ScratchConnectionError, e:
            print(e)
            exit(1)

    def run(self):
        s = self.s
        while True:
            try:
                message = s.receive(2)
            except s.ScratchConnectionError, e:
                print(e)
                exit(1)
            print 'Scratch:',message
            server.send( message )
    
    def send(self, message):
        s = self.s
        message = s.parse_message(message)
        
        print message
        if len( message['broadcast'] ) == 1:
            s.broadcast( message['broadcast'][0] )
        elif len( message['sensor-update'] ) == 1:
            s.sensorupdate( message['sensor-update'] )
    
class Server(threading.Thread):
    
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.s.connect((ip, port))
    
    def run(self):
        s = self.s
        while True:
            try:
                message = s.recv(1024)
                if message == None:
                    exit(1)
            except:
                exit(1)
            print 'Server:',message
            scratch.send(message)
    
    def send(self, message):
        self.s.send(message)

server = Server(SHOST, SPORT) # Start up the class for Server
server.start() # This starts the 'run' function on the class as well.

scratch = Client() # Start up the class for Scratch
scratch.start() # This starts the 'run' function.