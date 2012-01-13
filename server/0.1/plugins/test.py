# Test Plugin

class Server(object):
    
    def __init__(self):
        self.number_of_tests = 0

class Plugin(object):
    
    def __init__(self, client, server):
        self.client = client
        self.server = server.plugin_servers['test']
    
    def broadcast(self, message):
        owner = self.client
        if message == 'test':
            self.server.number_of_tests += 1
            owner.send_sensor( 'number of tests', str( self.server.number_of_tests ) )
            owner.send_broadcast( "You have added a test." )
        else:
            print message
    
    def sensor(self, name, value):
        pass
        