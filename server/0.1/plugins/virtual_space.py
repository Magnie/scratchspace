# Virtual Space Plugin
import threading
import math

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
        
        # Player Settings
        self.name = ''
        
        # Physics Engine
        self.physics = Physics(self)
    
    def space_parse(self, message):
        message = message.split(' ')
        request = message[0]
        args = message[1:]
        del message
        if request == 'name':
            self.name = args[0]
        elif request == 'forward':
            self.forward = 1
        elif request == 'not forward':
            self.forward = 0

class Physics(threading.Thread):
    
    def __init__(self, owner):
        threading.Thread.__init__(self)
        self.owner = owner
        
        self.xpos = 0
        self.ypos = 0
        self.xvel = 0
        self.yvel = 0
        
        self.angle = 0
        
        self.accel = 0.1
        
        self.inertia = 0

        self.max_speed = 2
        self.min_speed = 0
        self.current_speed = 0
        
        self.alive = 1
    
    def run(self):
        while self.alive:
            self.update_controls()
            self.update_ship_pos()
    
    def update_controls(self):
        if self.owner.move_forward == 1:
            move_forward()
        if self.owner.turn_right == 1:
            turn_right()
        if self.owner.turn_left == 1:
            turn_left()
    
    def move_forward(self):
        radians = (math.pi / 180) * self.angle
        temp_x_vel = self.xvel + (math.sin( radians ) * self.accel)
        temp_y_vel = self.yvel + (math.cos( radians ) * self.accel)
        
        if ( math.abs(temp_x_vel) + math.abs(temp_y_vel) ) < self.max_speed:
            self.xvel = temp_x_vel
            self.yvel = temp_y_vel
        
    def update_ship_pos(self):
        self.xpos += self.xvel
        self.ypos += self.yvel