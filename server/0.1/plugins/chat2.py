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

import urllib2 as urllib


# Server
class Server(object):
    
    def __init__(self):
        # 'room' : {'ranks' : {'user' : 'rank'}, 'users' : []}
        self.chat_rooms = { 'main' : {'ranks' : {}, 'users' : []} }
        
        # 'username' : {'rank' : 'rank', 'hash' : 'hash'}
        self.chat_accounts = {'Magnie' : ['*', '']}
        
        # 'username' : user
        self.chat_users = {}
        
        # IP Ban List '0.0.0.0'
        self.banned_ips = []
        
        # Guest counter is to keep users from having the same name
        self.guest_counter = 0
    
# Client
class Plugin(object):
    
    def __init__(self, client, server):
        if client.address[0] in server.banned_ips:
            client.not_plugin('chat2')
            return
        self.cowner = client
        
        # Set the "server" it's using.
        self.server = server.plugin_servers['chat2']
        
        # Client Stuff
        self.server.guest_counter += 1
        self.name = 'Guest' + str(self.server.guest_counter)
        
        # Add itself to the chat_users list
        self.server.chat_users[self.name] = self
        
        # Set the ranks for the channel and server
        self.room_rank = '-'
        self.global_rank = '-'
        
        self.authenticated = False
        
        # Add the user to the default room 'main'
        self.join_room('main')
    
    def broadcast(self, raw_message):
        message = raw_message.split(' ')
        request = message[0]
        args = message[1:]
        
        if request == 'switch-room' and len(args) == 1:
            self.switch_room(args[0])
        
        elif request == 'switch-name' and len(args) == 1:
            self.switch_name(args[0])
        
        elif request == 'send' and len(args) > 0:
            self.room_message(' '.join(args))
        
        elif request == 'auth' and len(args) == 2:
            pass
        
        elif request == 'scratch-auth' and len(args) == 2:
            self.scratch_auth(args[0], args[1])
        
        elif request == 'mute' and len(args) == 1:
            self.mute_user(args[0])
        
        elif request == 'force-kill' and len(args) == 1:
            self.force_kill(args[0])
        
        elif request == 'user-list' and len(args) == 1:
            self.user_list()
        
        elif request == 'whisper' and len(args) > 1:
            self.user_message(args[0], ' '.join(args[1:]))
    
    def sensor(self, name, value):
        pass
    
    def disconnect(self):
        self.leave()
    
    def send_broadcast(self, message):
        # Send a broadcast to the client
        self.cowner.send_broadcast(message)
    
    def send_sensor(self, name, value):
        # Send a sensor-update to the client.
        self.cowner.send_sensor( name, value )

    # Server Stuff
    
    def switch_room(self, new_room):
        old_room = self.room
        
        self.part_room(old_room)
        self.join_room(new_room)
    
    def join_room(self, room):
        if room in self.server.chat_rooms:
            chat_room = self.server.chat_rooms[room]
            if self.name in chat_room['ranks'] and self.authenticated:
                self.room_rank = chat_room['ranks'][self.name]
            else:
                self.room_rank = self.global_rank
        else:
            self.server.chat_rooms[room] = {'ranks' :
                                                {
                                                self.name : '^'
                                                },
                                            'users' : []
                                           }
            chat_room = self.server.chat_rooms[room]
            self.room_rank = chat_room['ranks'][self.name]
        
        chat_room['users'].append(self.name)
        self.room = room
        self._message_room(self.room, self.name + ' has joined!')
        print self.name, 'has joined', self.room + '!'
    
    def part_room(self, old_room):
        old_chat_room = self.server.chat_rooms[old_room]
        if self.name in old_chat_room:
            old_chat_room['users'].remove(self.name)
            self._message(old_room, self.name + ' has left.')
            
            print self.name, 'has left', old_room + '!'
    
    def switch_name(self, new_name):
        chat_users = self.server.chat_users
        if new_name not in chat_users:
            old_name = self.name
            self.name = new_name
            chat_room = self.server.chat_rooms[self.room]
            chat_room['users'].remove(old_name)
            chat_room['users'].append(new_name)
            
            del self.server.chat_users[old_name]
            self.server.chat_users[new_name] = self
            
            self._message_room(self.room,
                          old_name + ' renamed to ' + new_name)
            
            print old_name, 'has switched to', new_name + '!'
    
    def scratch_auth(self, username, password):
        if scratch_authenticate(username, password):
            self.authenticated = True
            self.global_rank = self.server.chat_accounts[username][0]
            
            print self.name, 'has authenticated as', username + '!'
    
    def leave(self):
        try:
            self.part_room(self.room)
        except Exception, e:
            print e
        del self.server.chat_users[self.name]
        
        print self.name, 'has disconnected!'
    
    def room_message(self, message):
        if self.room_rank not in '#':
            full_message = self.room_rank + self.name + ': ' + message
            self._message_room(self.room, full_message)
    
    def user_message(self, user, message):
        if self.room_rank and self.global_rank not in '#':
            full_message = self.name + ': ' + message
            self._message_user(user, message)
    
    def _message_room(self, room, message):
        room = self.server.chat_rooms[room]['users']
        print room + ':', message
        for user in room:
            user = self.server.chat_users[user]
            user.send_sensor('chat', message)
            user.send_broadcast('new_message')
    
    def _message_user(self, user, message):
        if user in self.chat_users:
            print user + ':', message
            user = self.server.chat_users[user]
            user.send_sensor('chat', message)
            user.send_broadcast('new_message')
    
    def mute_user(self, name):
        if self.room_rank in '*~^@':
            if name in self.server.chat_rooms[self.room]['users']:
                self.server.chat_users[name].room_rank = '#'
                
                print name, 'has been muted by', self.name + '!'
    
    def perma_mute(self, name):
        if self.room_rank in '*~^@':
            self.server.chat_rooms[self.room]['ranks'][name] = '#'
            
            print name, 'has been muted by', self.name + '!'
    
    def change_room_rank(self, name, new_rank):
        if self.room_rank in '*~^@':
            chat_room = self.server.chat_rooms[self.room]
            if self.room_rank == '*':
                chat_room['ranks'][name] = new_rank
            
            elif self.room_rank == '~':
                if new_rank in '^@+!#':
                    chat_room['ranks'][name] = new_rank
            
            elif self.room_rank == '^':
                if new_rank in '^@+!#':
                    chat_room['ranks'][name] = new_rank
            
            elif self.room_rank == '@':
                if new_rank in '+!#':
                    chat_room['ranks'][name] = new_rank
            
            print self.name, 'has changed', self.name + '\'s rank to', new_rank + '!'
    
    def force_kill(self, name):
        if self.global_rank in '*':
            if name in self.server.chat_users:
                self.server.chat_users[name].leave()
                if name in self.server.chat_users:
                    del self.server.chat_users[name]
    
    def user_list(self):
        message = ''
        for user in self.server.chat_rooms['users']:
            message += user + ', '
        message = message[:-1] + '.'
        self._message_user(self.name, message)

def scratch_authenticate(username, password):
    #username = urllib.urlencode(username)
    #password = urllib.urlencode(password)
    string = "http://scratch.mit.edu/api/authenticateuser?username="
    string = string, username, "&password=" , password
    string = "".join(string)
    fp = urllib.urlopen(string)
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