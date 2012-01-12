# Test Plugin

class Plugin(object):
    
    def __init__(self, client, server):
        self.client = client
        self.server = server
    
    def broadcast(self, message):
        owner = self.owner
        if message == 'test':
            owner.send_broadcast( "test" )
        else:
            print message
    
    def sensor(self, name, value):
        pass
        