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
import hashlib

# Server
class Server(object):
    
    def __init__(self):
        # 'room' : {'ranks' : {'user' : 'rank'},
        #           'users' : [],
        #           'flags' : 'flags'}
        self.chat_rooms = { 'main' : {'ranks' : {},
                                      'flags' : '',
                                      'users' : []} }
        
        # 'username' : {'rank' : 'rank', 'hash' : 'hash'}
        self.chat_accounts = {'Magnie' : {'rank' : '*', 'hash' : ''}}
        
        # 'username' : user
        self.chat_users = {}
        
        # IP Ban List '0.0.0.0'
        self.banned_ips = []
        
        # Guest counter is to keep users from having the same name
        self.guest_counter = 0
        
        # Other Settings
        self.pre_salt = 'ABCHDasdfjCHdsaKGLs7984@W(&*$#245kjasdfjkh^%E(KJa*T$%EKJsdfnjdsflj#WREfd'
        self.suf_salt = 'tNCJLSDfgjlaSLDFahsuiKUHF;fsdla(EAaw8e7uifj@#%(*sad87($#%WKJEfsd88793w24'
        self.sec_salt = 'DJKSLAKSDIO329a8sdfjkh34%(*a786MV$V(Abidjlkjhtb4978Q$#*rn02qienQ#$(R#Qkj'
    
# Client
class Plugin(object):
    
    def __init__(self, client, server):
        ip = client.address[0]
        if ip in server.banned_ips:
            client.not_plugin('chat2')
            return
        self.cowner = client
        
        # Strings, etc
        self.messages = {
                'auth_1' : '{0} has authenticated as {1}!',
                'auth_0' : '{0} has failed to authenticated as {1}!',
                'name' : '{0} renamed to {1}!',
                'rank' : '{0} changes {1}\'s rank to {2}!',
                
                'mute' : '{0} has muted {1}!',
                'join' : '{0} has joined {1}!',
                'part' : '{0} has parted {1}!',
                'send' : '[{0}] {1} > {2}: {3}'
                }
        
        self.bad_words = []
        self.good_words = []
        
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
        print '{0} has connected with IP: {1}!'.format(self.name, ip)
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
            self.auth(args[0], args[1])
        
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
        
        elif request == 'flags' and len(args) == 1:
            pass
    
    def sensor(self, name, value):
        pass
    
    def disconnect(self):
        self.leave()
    
    def send_broadcast(self, message):
        # Send a broadcast to the client
        self.cowner.send_broadcast(message)
    
    def send_sensor(self, name, value):
        # Send a sensor-update to the client.
        self.cowner.send_sensor(name, value)

    # Server Stuff
    
    def switch_room(self, new_room):
        old_room = self.room
        
        if new_room not in self.server.chat_rooms:
            if self.global_rank not in '*~':
                return
        
        if '%' in self.server.chat_rooms[new_room]['flags']:
            if self.global_rank not in '%~@^':
                return
        
        if '~' in self.server.chat_rooms[new_room]['flags']:
            if self.global_rank not in '~*':
                return
        
        self.part_room(old_room)
        self.join_room(new_room)
    
    def join_room(self, room):
        name = self.name
        if room in self.server.chat_rooms:
            chat_room = self.server.chat_rooms[room]
            if name in chat_room['ranks'] and self.authenticated:
                self.room_rank = chat_room['ranks'][name]
            else:
                self.room_rank = self.global_rank
        else:
            self.server.chat_rooms[room] = {'ranks' :
                                                {
                                                name : '^'
                                                },
                                            'users' : []
                                           }
            chat_room = self.server.chat_rooms[room]
            self.room_rank = chat_room['ranks'][name]
        
        chat_room['users'].append(name)
        self.room = room
        self._message_room(self.room, name + ' has joined!')
        print self.messages['join'].format(name, room)
    
    def part_room(self, old_room):
        print 'parting'
        name = self.name
        old_chat_room = self.server.chat_rooms[old_room]
        if name in old_chat_room['users']:
            print 'in room, removing'
            old_chat_room['users'].remove(name)
            self._message_room(old_room, name + ' has left.')
            print 'removed'
            
            print self.messages['part'].format(name, old_room)
    
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
            
            print self.messages['name'].format(old_name, new_name)
    
    def scratch_auth(self, username, password):
        if scratch_authenticate(username, password):
            self.authenticated = True
            self.global_rank = self.server.chat_accounts[username]['rank']
            
            print self.messages['auth_1'].format(self.name, username)
        else:
            print self.messages['auth_0'].format(self.name, username)
    
    def auth(self, username, password):
        if username in self.server.chat_accounts:
            chat_accounts = self.server.chat_accounts
            password = self.hash(password)
            
            if chat_accounts[username]['hash'] == password:
                self._auth(username)
        
        if self.authenticated:
            print self.messages['auth_1'].format(self.name, username)
        else:
            print self.messages['auth_0'].format(self.name, username)
    
    def _auth(self, username):
        self.authenticated = True
        self.global_rank = self.server.chat_accounts[username][0]
    
    def leave(self):
        try:
            self.part_room(self.room)
        except Exception, e:
            print e
        del self.server.chat_users[self.name]
        
        print self.name, 'has disconnected!'
    
    def room_message(self, message):
        if '+' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*+%@^':
                pass
            else:
                return
        
        if '%' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*%@^':
                pass
            else:
                return
        
        if '@' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*@^':
                pass
            else:
                return
        
        if '^' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*^':
                pass
            else:
                return
        
        censor = self.censor_message(message)
        if censor:
            message = censor
        else:
            return
        
        name = self.name
        if self.room_rank not in '#':
            full_message = self.room_rank + name + ': ' + message
            self._message_room(self.room, full_message)
    
    def user_message(self, user, message):
        if self.room_rank and self.global_rank not in '#':
            full_message = self.name + ': ' + message
            self._message_user(user, message)
    
    def _message_room(self, room_name, message):
        room = self.server.chat_rooms[room_name]['users']
        print self.messages['send'].format('0:0:0',
                                               self.name,
                                               room_name,
                                               message)
        
        for user in room:
            try:
                user = self.server.chat_users[user]
                user.send_sensor('chat', message)
                user.send_broadcast('new_message')
            except KeyError:
                room.remove(user)
    
    def _message_user(self, user, message):
        if user in self.chat_users:
            user = self.server.chat_users[user]
            user.send_sensor('chat', message)
            user.send_broadcast('new_message')
            
            print self.messages['send'].format('0:0:0',
                                               self.name,
                                               user,
                                               message)
    
    def censor_message(self, raw_message):
        flags = self.server.chat_rooms[self.room]['flags']
        message = raw_message.split(' ')
        
        if '0' in flags:
            for word in message:
                if word in good_words:
                    return raw_message
            
            return 0
        
        elif '1' in flags:
            for bad_word in self.bad_words:
                if bad_word in raw_message:
                    return 0
            return raw_message
        
        elif '2' in flags:
            for word in message:
                for bad_word in self.bad_words:
                    if bad_word in word:
                        if word not in self.good_words:
                            return 0
            return raw_message
        
        elif '3' in flags:
            for bad_word in self.bad_words:
                if bad_word in raw_message:
                    raw_message = raw_message.replace(bad_word, '*')
            return raw_message
        
        else:
            return raw_message
                
    def mute_user(self, name):
        if self.room_rank in '*~^@':
            if name in self.server.chat_rooms[self.room]['users']:
                self.server.chat_users[name].room_rank = '#'
                
                print self.messages['mute'].format(name, self.name)
    
    def perma_mute(self, name):
        if self.room_rank in '*~^@':
            self.server.chat_rooms[self.room]['ranks'][name] = '#'
            
            print self.messages['mute'].format(name, self.name)
    
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
            
            print self.messages['rank'].format(self.name, name, new_rank)
    
    def hash(self, hash):
        pre_salt = self.server.pre_salt
        suf_salt = self.server.suf_salt
        sec_salt = self.server.sec_salt
        
        hash = hashlib.sha512(pre_salt + hash + suf_salt)
        hash = hash.digest()
        hash = hashlib.sha256(pre_salt + hash + suf_salt)
        hash = hash.digest()
        hash = hashlib.sha512(sec_salt + hash)
        return hash.digest()
    
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
    string = string + username + "&password=" + password
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