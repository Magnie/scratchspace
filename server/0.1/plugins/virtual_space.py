# Virtual Space Plugin
import threading
import math
import time

# Server
class Server(object):
    
    def __init__(self):
        self.universes = {}
    
    def assign(self, player):
        for universe in self.universes:
            universe = self.universes[universe]
            if len( universe.players ) < universe.max_players:
                universe.players.append( player )
                return 'Added'
        return 'No universe available.'
    
    def create_uni(self, name, max_players=12):
        if name in self.universes:
            return 'It already exists'
        else:
            self.universes[name] = Universe()
            return 'Universe created.'
    
    def uni_exist(self, name):
        if name in self.universes:
            return True
        else:
            return False

class Universe(object):

    def __init__(self, max_players=12):
        self.solar_systems = []
        self.players = []
        self.max_players = max_players

class Universe_Updater(threading.Thread):
    
    def __init__(self, universe, update_speed=0.2):
        threading.Thread.__init__(self)
        self.universe = universe
        self.update_speed = update_speed
    
    def run(self):
        pass
    
    def update(self):
        players_to_update = []
        for player in self.universe.players:
            players_to_update.append( [player.physics.xpos, player.physics.ypos, player.physics.angle, player.owner] )
        
        # Update each client with the locations of all the players.
        for client in players_to_update:
            con = client[3] # Connection
            i = 0
            for player in players_to_update:
                pid = 'p'+str(i) # Player ID
            
                x = player[0] # X position
                y = player[1] # Y position
                d = player[2] # Direction
            
                # Send the location and player ID to the client.
                con.update_sensor(pid+'x', str(x))
                con.update_sensor(pid+'y', str(y))
                con.update_sensor(pid+'d', str(d))
                i += 1

class SolarSystem(object):
    
    def __init__(self):
        pass

class Planet(object):

    def __init__(self):
        pass

        
# Client
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
        
        # Spaceship Controls
        self.thrust_forward = 0
        self.turn_left = 0
        self.turn_right = 0
        self.fire_shot = 0
    
    def space_parse(self, message):
        message = message.split(' ')
        request = message[0]
        args = message[1:]
        del message
        if request == 'name':
            self.name = args[0]
        elif request == 'forward true':
            self.thrust_forward = 1
        elif request == 'forward false':
            self.thrust_forward = 0
        
        elif request == 'left true':
            self.turn_left = 1
        elif request == 'left false':
            self.turn_left = 0
        
        elif request == 'right true':
            self.turn_right = 1
        elif request == 'right false':
            self.turn_right = 0
        
        elif request == 'shot true':
            self.fire_shot = 1
        elif request == 'shot false':
            self.fire_shot = 0

class Physics(threading.Thread):
    
    def __init__(self, owner, update_speed=0.2):
        threading.Thread.__init__(self)
        self.owner = owner
        
        self.xpos = 0
        self.ypos = 0
        self.xvel = 0
        self.yvel = 0
        
        self.angle = 0
        
        self.accel = 0.1
        
        self.inertia = 0

        self.max_speed = 4
        self.min_speed = 0
        self.current_speed = 0
        
        self.alive = 1
        
        self.update_speed = update_speed
    
    def run(self):
        if self.update_speed > 0:
            self.updater_limited()
        else:
            self.updater_no_limit()
    
    def updater_limited(self):
        last_update = time.time()
        while self.alive:
            current_time = time.time()
            if current_time >= (last_update + self.update_speed):
                self.update_controls()
                self.update_ship_pos()
                last_update = time.time()
                current_time = time.time()
    
    def updater_no_limit(self):
        while self.alive:
            self.update_controls()
            self.update_ship_pos()
    
    def update_controls(self):
        if self.owner.thrust_forward == 1:
            move_forward()
        if self.owner.turn_right == 1:
            turn_right()
        if self.owner.turn_left == 1:
            turn_left()
    
    def move_forward(self):
        radians = (math.pi / 180) * self.angle
        temp_x_vel = self.xvel + (math.sin( radians ) * self.accel)
        temp_y_vel = self.yvel + (math.cos( radians ) * self.accel)
        
        if ( math.abs(temp_x_vel) + math.abs(temp_y_vel) ) <= self.max_speed:
            self.xvel = temp_x_vel
            self.yvel = temp_y_vel
    
    def turn_left():
        self.angle -= 1
        if self.angle < 0:
            self.angle += 360
    
    def turn_right():
        self.angle += 1
        if self.angle > 360:
            self.angle -= 360
        
    def update_ship_pos(self):
        self.xpos += self.xvel
        self.ypos += self.yvel