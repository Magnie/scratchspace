# Virtual Space Plugin

class Plugin(object):
    
    def __init__(self, client, server):
        self.cowner = client
        self.sowner = server
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
    
    def broadcast(self, message):
        if message == 'speed up':
            if self.current_speed >= self.max_speed:
                pass
            else:
                self.current_speed += self.accel

            self.send_sensor( "p1", str(self.y) )
        else:
            print message
    
    def sensor(self, name, value):
        pass
    
    def send_broadcast(self, message):
        self.cowner.send_broadcast( message )
    
    def send_sensor(self, name, value):
        self.cowner.send_sensor( name, value )