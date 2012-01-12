# Virtual Space Plugin

class Plugin(object):
    
    def __init__(self, owner):
        self.owner = owner
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
        owner = self.owner
        if message == 'speed up':
            if self.current_speed >= self.max_speed:
                pass
            else:
                self.current_speed += self.accel
            
            if
            owner.send_sensor( "p1", str(self.y) )
        else:
            print message
    
    def sensor(self, name, value):
        pass