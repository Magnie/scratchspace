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
                print pid, player
                if player == None:
                    universe.add_player(pid, client)
                    return 'Player added.'
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
        self.weapons =  { 
                            0 : {
                                    'name' : 'Light Particle Blaster',
                                    'type' : 0,
                                    'shield_damage' : 3,
                                    'armour_damage' : 3
                                },
                         
                            1 : {
                                    'name' : 'Beam Cannon',
                                    'type' : 2,
                                    'shield_damage' : 6,
                                    'armour_damage' : 0
                                }
                        }
        
        # Settings
        self.max_players = max_players
        
        # Create all the needed data.
        for player in xrange(0, self.max_players):
            self.players[str(player)] = None
        
        for i in xrange(0, 10):
            self.solar_systems.append(SolarSystem(str(i)))
        
        # Universe Updater
        self.updater = UniverseUpdater(self)
        self.updater.start()
    
    def del_player(self, pid):
        self.players[pid] = None
    
    def add_player(self, pid, player):
        self.players[pid] = player
        self.players[pid].universe = self
        self.players[pid].solar_system = self.assign_solar_system(pid)
        self.players[pid].player_id = pid
        
    def assign_solar_system(self, pid):
        return self.solar_systems[0]

        
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
            if player == None:
                continue
            player.physics.update()
    
    def update_player(self, client):
        players_to_update = []
        con = client.owner
        solar_system = client.solar_system
        
        # Get the neccessary info and put it into a list
        for player in self.universe.players:
            player = self.universe.players[player]
            if player == None:
                continue
            players_to_update.append( [player.owner,
                                        player.physics.xpos,
                                        player.physics.ypos,
                                        player.physics.angle,
                                        player.solar_system,
                                        player.player_id,
                                        player.physics.visible] )
        
        # Update each client with the locations of all the players.
        for player in players_to_update:
              
            # Make sure the player is in the same solar system.
            if player[4] != solar_system:
                continue
                
            pid = 'p'+player[5] # Player ID
            
            x = player[1] # X position
            y = player[2] # Y position
            d = player[3] # Direction
            v = player[6] # Visible
            
            # Send the location and player ID to the client.
            con.send_sensor(pid+'x', str(x))
            con.send_sensor(pid+'y', str(y))
            con.send_sensor(pid+'d', str(d))
            con.send_sensor(pid+'v', str(v))
        con.send_broadcast('~update')

                
class SolarSystem(object):
    
    def __init__(self, name):
        self.name = name

        
class Planet(object):

    def __init__(self):
        self.xpos = 0
        self.ypos = 0
        self.name = 'N/A'
        self.type = 0 # Any number.

        
# Client
class Plugin(object):
    
    def __init__(self, client, server):
        self.cowner = client
        
        # Set the "server" it's using.
        self.virtual_space = server.plugin_servers['virtual_space']
        
        # Create the spaceship
        self.spaceship = Spaceship(self)
        
        # Assign the spaceship/player to a universe and solar system.
        self.virtual_space.assign(self.spaceship)
    
    def broadcast(self, message):
        self.spaceship.space_parse(message)
    
    def sensor(self, name, value):
        pass
    
    def disconnect(self):
        self.spaceship.universe.del_player(self.spaceship.player_id)
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
        self.universe = None
        self.solar_system = None
        self.player_id = None
        
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
        print request, args
        
        # Checks if the client wants to change their name.
        if request == 'name':
            self.name = args[0]
        
        # Checks if they want to move their ship forward.
        elif request == 'forward-true':
            self.thrust_forward = 1
        
        elif request == 'forward-false':
            self.thrust_forward = 0
        
        # Checks if they want to turn left.
        elif request == 'left-true':
            self.turn_left = 1
        elif request == 'left-false':
            self.turn_left = 0
        
        # Checks if they want to turn right.
        elif request == 'right-true':
            self.turn_right = 1
        elif request == 'right-false':
            self.turn_right = 0
        
        # Checks if they want to shoot a laser.
        elif request == 'shot-true':
            self.fire_shot = 1
        elif request == 'shot-false':
            self.fire_shot = 0
        
        # Any Other Utilities
        elif request == 'player-id':
            self.owner.send_sensor('pid', self.player_id)
            self.owner.send_broadcast('~pid')
        
        elif request == 'update':
            self.universe.updater.update_player(self)
        
        elif request == 'get-vars':
            counter = 0
            for i in self.universe.players:
                self.owner.send_sensor('p'+str(counter)+'x', '0')
                self.owner.send_sensor('p'+str(counter)+'y', '0')
                self.owner.send_sensor('p'+str(counter)+'d', '0')
                self.owner.send_sensor('p'+str(counter)+'v', '0')
                
                self.owner.send_sensor('w'+str(counter)+'x', '0')
                self.owner.send_sensor('w'+str(counter)+'y', '0')
                self.owner.send_sensor('w'+str(counter)+'d', '0')
                self.owner.send_sensor('w'+str(counter)+'v', '0')
                
                counter += 1

            
class Physics(object): # class Physics(threading.Thread):
    
    def __init__(self, owner):
        #threading.Thread.__init__(self)
        self.owner = owner
        
        # Settings
        
        # Physical properties of the player and ship
        self.xpos = 0
        self.ypos = 0
        self.angle = 0
        self.radians = (math.pi / 180) * self.angle
        self.visible = 1 # Are they visible? 1 = True, 0 = False
        
        # Spaceship limitations
        self.accel = 0.1
        self.inertia = 0
        self.max_speed = 4
        self.min_speed = 0
        self.turn_speed = 4
        
        # Set the player as alive
        self.alive = 1
        
        # Physics
        self.xvel = 0
        self.yvel = 0
        self.current_speed = 0
        
        # Weapons
        self.weapon = Weapon()
    
    def run(self):
        if self.update_speed > 0:
            self.updater_limited()
        else:
            self.updater_no_limit()
    
    def update(self):
        self.update_controls()
        self.update_ship_pos()
    
    def update_controls(self):
        # Update anything that needs updating.
        if self.owner.thrust_forward:
            self.move_forward()
            
        if self.owner.turn_right:
            self.turn_right()
            
        if self.owner.turn_left:
            self.turn_left()
            
        if self.owner.fire_shot:
            self.fire_shot()
    
    def move_forward(self):
        radians = (math.pi / 180) * self.angle
        temp_x_vel = self.xvel + (math.sin( self.radians ) * self.accel)
        temp_y_vel = self.yvel + (math.cos( self.radians ) * self.accel)
        
        if (abs(temp_x_vel) + abs(temp_y_vel) ) <= self.max_speed:
            self.xvel = temp_x_vel
            self.yvel = temp_y_vel
    
    def turn_left(self):
        self.angle -= self.turn_speed
        if self.angle < 0:
            self.angle += 360
        self.radians = (math.pi / 180) * self.angle
    
    def turn_right(self):
        self.angle += self.turn_speed
        if self.angle > 360:
            self.angle -= 360
        self.radians = (math.pi / 180) * self.angle
    
    def fire_shot(self):
        if not self.weapon.in_motion:
            weapon = self.weapon
            weapon.xpos = self.xpos
            weapon.ypos = self.ypos
            weapon.angle = self.angle
            weapon.radians = self.radians
            weapon.reset()
        
    def update_ship_pos(self):
        self.xpos += self.xvel
        self.ypos += self.yvel

class Weapon(object):

    def __init__(self):
    
        # Physical properties of the projectile.
        self.xpos = 0
        self.ypos = 0
        self.angle = 0
        self.radians = (math.pi / 180) * self.angle
        self.visible = 1 # Is it visible? 1 = True, 0 = False
        
        # Alive?
        self.alive = 1
        
        # Weapon Settings
        self.costume = 0 # Any number (depending on the client)
        self.type = 0 # 0 = Normal, 1 = Ignores Shields, 2 = Ignore Armour (can't destroy)
        self.shield_damage = 0 # Any number
        self.armour_damage = 0 # Any number
    
    def move_forward(self):
        radians = (math.pi / 180) * self.angle
        temp_x_vel = self.xvel + (math.sin( self.radians ) * self.accel)
        temp_y_vel = self.yvel + (math.cos( self.radians ) * self.accel)
        
        if (abs(temp_x_vel) + abs(temp_y_vel) ) <= self.max_speed:
            self.xvel = temp_x_vel
            self.yvel = temp_y_vel
    
    def collision_check(self, objects):
        mask = [(self.xpos + 10),
                (self.ypos + 10),
                (self.xpos - 10),
                (self.ypos - 10)]
        
        for object in objects:
            if object.xpos <= mask[0] and object.xpos >= mask[2]:
                if object.ypos <= mask[1] and object.ypos >= mask[3]:
                    if object.weapon != self:
                        object.collide()
                        self.alive = 0
                        break
    
    def reset(self):
        self.alive = 1
    
    def update_proj_pos(self):
        self.xpos += self.xvel
        self.ypos += self.yvel