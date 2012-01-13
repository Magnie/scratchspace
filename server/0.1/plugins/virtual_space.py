# Virtual Space Plugin

class Server(object):
    
    def __init__(self):
        self.spaceships = []

class Plugin(object):
    
    def __init__(self, client, server):
        self.cowner = client
        self.virtual_space = server.plugin_servers['virtual_space']
        self.spaceship = Spaceship(self)
        
        self.virtual_space.spaceships.append( self.spaceship )
    
    def broadcast(self, message):
        self.spaceship.space_parse(message)
    
    def sensor(self, name, value):
        pass
    
    def send_broadcast(self, message):
        self.cowner.send_broadcast( message )
    
    def send_sensor(self, name, value):
        self.cowner.send_sensor( name, value )
        
class Spaceship(object):
    
    def __init__(self, owner):
        self.owner = owner
        
        # Spaceship Settings
        self.xpos = 0
        self.ypos = 0
        self.ddir = 0
        
        self.accel = 0.1
        
        self.inertia = 0

        self.max_speed = 2
        self.min_speed = 0
        self.current_speed = 0

        self.xvel = 0
        self.yvel = 0
        
        # Player Settings
        self.name = ''
        
        # Physics Engine
    
    def space_parse(self, message):
        message = message.split(' ')
        request = message[0]
        args = message[1:]
        del message
        if request == 'name':
            self.name = args[0]
        elif request == 'forward':
            self