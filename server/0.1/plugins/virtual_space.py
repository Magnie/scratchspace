# Virtual Space Plugin
import threading
import math
import time


# Server
class Server(object):
    
    def __init__(self):
        self.universes = {}
        self.create_uni('main')
    
    def assign(self, client):
        # Go through all the universes and find
        # the first available spot and add the
        # player to it.
        for universe in self.universes:
            universe = self.universes[universe]
            for pid in universe.players:
                player = universe.players[pid]
                if player == None:
                    universe.add_player(pid, client)
                    return universe, pid
        return 'No universe available.'
    
    def create_uni(self, name, max_players=12):
        # Check if it already exists, if not, then create it.
        if self.uni_exist(name):
            return 'It already exists'
        else:
            self.universes[name] = Universe()
            return 'Universe created.'
    
    def uni_exist(self, name):
        # Check if the universe exists
        if name in self.universes:
            return True
        else:
            return False


class Universe(object):

    def __init__(self, max_players=12):
        
        # Data
        self.solar_systems = []
        self.players = {}
        
        # Settings
        self.max_players = max_players
        
        for player in xrange(0, self.max_players):
            self.players[str(player)] = None
        
        # Universe Updater
        self.updater = UniverseUpdater(self)
        self.updater.start()
    
    def del_player(self, pid):
        self.players[pid] = None
    
    def add_player(self, pid, player):
        self.players[pid] = player

        
class UniverseUpdater(threading.Thread):
    
    def __init__(self, universe, update_speed=0.2):
        threading.Thread.__init__(self)
        self.universe = universe # The universe it's assigned to.
        self.update_speed = update_speed # The speed "limit" of the script.
        self.alive = 1
    
    def run(self):
        last_update = time.time()
        while self.alive:
            current_time = time.time()
            if current_time >= (last_update + self.update_speed):
                self.update()
                last_update = time.time()
                current_time = time.time()
    
    def update(self):
        players_to_update = []
        
        # Get the neccessary info and put it into a list
        for player in self.universe.players:
            player = self.universe.players[player]
            players_to_update.append( [player.physics.xpos,
                                        player.physics.ypos,
                                        player.physics.angle,
                                        player.owner] )
        
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
        
        # Set the "server" it's using.
        self.virtual_space = server.plugin_servers['virtual_space']
        
        # Create the spaceship
        self.spaceship = Spaceship(self)
        
        # Assign the spaceship/player to a universe and solar system.
        self.universe, self.pid = self.virtual_space.assign(self.spaceship)
    
    def broadcast(self, message):
        self.spaceship.space_parse(message)
    
    def sensor(self, name, value):
        pass
    
    def disconnect(self):
        self.universe.del_player(self.pid)
        del self.spaceship.physics
    
    def send_broadcast(self, message):
        # Send a broadcast to the client
        self.cowner.send_broadcast(message)
    
    def send_sensor(self, name, value):
        # Send a sensor-update to the client.
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
        
        # Checks if the client wants to change their name.
        if request == 'name':
            self.name = args[0]
        
        # Checks if they want to move their ship forward.
        elif request == 'forward true':
            self.thrust_forward = 1
        
        elif request == 'forward false':
            self.thrust_forward = 0
        
        # Checks if they want to turn left.
        elif request == 'left true':
            self.turn_left = 1
        elif request == 'left false':
            self.turn_left = 0
        
        # Checks if they want to turn right.
        elif request == 'right true':
            self.turn_right = 1
        elif request == 'right false':
            self.turn_right = 0
        
        # Checks if they want to shoot a laser.
        elif request == 'shot true':
            self.fire_shot = 1
        elif request == 'shot false':
            self.fire_shot = 0

            
class Physics(threading.Thread):
    
    def __init__(self, owner, update_speed=0.2):
        threading.Thread.__init__(self)
        self.owner = owner
        
        # Settings
        
        # Location and direction of player
        self.xpos = 0
        self.ypos = 0
        self.angle = 0
        
        # Spaceship limitations
        self.accel = 0.1
        self.inertia = 0
        self.max_speed = 4
        self.min_speed = 0
        
        # Set the player as alive
        self.alive = 1
        
        # Update speed "limit"
        self.update_speed = update_speed
        
        # Physics
        self.xvel = 0
        self.yvel = 0
        self.current_speed = 0
    
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
        # Update anything that needs updating.
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