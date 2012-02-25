# Chat Plugin
# By: Magnie (http://scratch.mit.edu/users/Magnie)

# List of ranks:
#
# * = Awesome Owner
# _blank_ = Server Ninja
# ~ = Global Mod
# % = Special Person
# ^ = Channel Owner 
# @ = Channel Mod
# + = Authenticated
# - = Guest/Unauthenticated
# ! = Failed Login
# # = Muted


# Server
class Server(object):
    
    def __init__(self):
        self.chat_rooms = {} # 'room name' : ['user 1', 'user 2']
        self.room_ranks = {} # 'room name' : {'user':'rank'}
        self.chat_accounts = {} # 'username' : ['rank', 'hash']
        self.chat_users = {} # 'username' : ['rank', 'room', user]
    
    def post_message(self, name, message):
        room = self.get_room(name)
        rank = self.get_rank(name)
        
        if rank not in '#':
            full_message = rank + name + ': ' + message
        
            self.send_message(room, full_message)
    
    def send_message(self, room, full_message):
        for user in room:
            user.send_sensor('chat', full_message)
            user.send_broadcast('new_message')
    
    def join_room(self, name, room, client):
        if name in self.room_ranks[room]:
            rank = self.room_ranks[room][name]
        else:
            rank = self.chat_users[name][0]
        
        self.chat_rooms.append(name)
        self.chat_users[name] = [rank, room, client]
        self.send_message(room, name+' has joined!')
    
    def part_room(self, name, room):
        self.chat_rooms[room].remove(name)
        self.send_message(room, name+' has left!')
    
    def authenticate(self, name, password):
        pass
    
    def scratch_auth(self, name, password):
        if scratch_authenticate(name, password):
            self.chat_users[name][0] = '%'
            return True
        else:
            self.chat_users[name][0] = '!'
            return False
    
    def switch_name(self, name, new_name):
        if new_name in self.chat_users:
            return False
        else:
            room = self.chat_users[name][1]
            client = self.chat_users[name][2]
            del self.chat_users[name]
            self.chat_rooms[room].remove(name)
            name = new_name
            
            self.chat_users[name] = ['-', room, client]
            self.chat_rooms[room].append(name)
            return True
    
    def change_rank(self, name, new_rank):
        room = self.get_room(name)
        self.room_ranks[room][name] = new_rank
            
    def get_rank(self, name):
        room = self.get_room(name)
        rank = self.room_ranks[room][name]
        return rank
    
    def get_room(self, name):
        room = self.chat_users[name][1]
        return room

    def leave(self, name):
        del self.part_room(name, self.get_room(name))
        del self.chat_users[name]
    
    def mute(self, muter, muted):
        if self.get_rank(muter) is in "*~^@":
            room = self.get_room(muter)
            self.change_rank(muted, '#')
        
# Client
class Plugin(object):
    
    def __init__(self, client, server):
        self.cowner = client
        
        # Set the "server" it's using.
        self.server = server.plugin_servers['chat']
        self.name = 'Guest'
        self.server.join(self.name, 'main', self)
        
    
    def broadcast(self, raw_message):
        message = raw_message.split(' ')
        request = message[0]
        args = message[1:]
        
        if request == 'join':
            self.server.join_room(self.name, args[0])
        
        elif request == 'part':
            self.server.part_room(self.name, args[0])
        
        elif request == 'send':
            self.server.send(self.name, ' '.join(args))
        
        elif request == 'name':
            if self.server.switch_name(args[0]):
                self.name = args[0]
            else:
                pass
        
        elif request == 'auth':
            pass
        
        elif request == 'scratch-auth':
            if self.server.scratch_auth(self.name, ' '.join(args)):
                self.server.post_message(self.name, 'has joined!')
            else:
                pass
        
        elif request == 'mute':
            self.server.mute(args[0])
    
    def sensor(self, name, value):
        pass
    
    def disconnect(self):
        self.server.leave(self.name)
    
    def send_broadcast(self, message):
        # Send a broadcast to the client
        self.cowner.send_broadcast(message)
    
    def send_sensor(self, name, value):
        # Send a sensor-update to the client.
        self.cowner.send_sensor( name, value )


def scratch_authenticate(username, password):
    username = urllib.urlencode(username)
    password = urllib.urlencode(password)
    string = "http://scratch.mit.edu/api/authenticateuser?username=", username, "&password=" , password
    string = "".join(string)
    fp = urllib.request.urlopen(string)
    result = fp.read()
    fp.close()
    result = result.decode("utf8")
    if result == ' \r\nfalse':
        return False
    else:
        result = result.split(':')
        if result[2] == 'blocked':
            return False
        else:
            return True