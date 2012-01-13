# Test Plugin
# This is an example plugin for the server.

# What it does is ignore all messages except 'test'
# and every time a client sends 'test' the count is
# increased by one. Then it sends the amount of
# tests that have been sent with a broadcast
# 'You have added a test.' to the client.

class Server(object):
    
    def __init__(self):
        self.number_of_tests = 0 # The counter

class Plugin(object):
    
    def __init__(self, client, server):
        self.client = client
        self.server = server.plugin_servers['test'] # Set the server to the "server" of the counter
    
    def broadcast(self, message):
        owner = self.client
        if message == 'test':
            # Increase the counter by one.
            self.server.number_of_tests += 1
            # Send the value of the counter to the client.
            owner.send_sensor( 'number of tests', str( self.server.number_of_tests ) )
            # Send a broadcast that it has been updated.
            owner.send_broadcast( "You have added a test." )
        else:
            print message
    
    def sensor(self, name, value):
        pass
        