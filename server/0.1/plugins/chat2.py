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

import urllib
import hashlib
import cPickle

from time import strftime

# Server
class Server(object):
    
    def __init__(self):
        # 'room' : {'ranks' : {'user' : 'rank'},
        #           'users' : [],
        #           'flags' : 'flags'}
        self.chat_rooms = { 'scratch' : {'ranks' : {},
                                         'flags' : '3',
                                         'motd' : 'Welcome to the Scratch chat room!',
                                         'users' : []} }
        
        # 'username' : {'rank' : 'rank', 'hash' : 'hash'}
        self.chat_accounts = {'Magnie' : {'rank' : '*',
                                          'hash' : '',
                                          'posts' : 0}}
        
        # 'username' : user
        self.chat_users = {}
        
        # IP Ban List '0.0.0.0'
        self.banned_ips = []
        
        # Guest counter is to keep users from having the same name
        self.guest_counter = 0
        
        # Other Settings
        self.pre_salt = 'ABCHDasdfjCHdsaKGLs7984@W(&*$#245kjasdfjkh^\
                        %E(KJa*T$%EKJsdfnjdsflj#WREfd'
        
        self.suf_salt = 'tNCJLSDfgjlaSLDFahsuiKUHF;fsdla(EAaw8e7uifj\
                        @#%(*sad87($#%WKJEfsd88793w24'
        
        self.sec_salt = 'DJKSLAKSDIO329a8sdfjkh34%(*a786MV$V(Abidjlk\
                        jhtb4978Q$#*rn02qienQ#$(R#Qkj'
        
        self.load_data()
        self.save_data()
    
    def load_data(self):
        try:
            data_file = open('chat.data', 'r')
            data = cPickle.load(data_file)
            data_file.close()
            
            self.chat_rooms = data['chat_rooms']
            self.chat_accounts = data['chat_accounts']
            
        except IOError, e:
            print e
    
    def save_data(self):
        try:
            data = {}
            data['chat_rooms'] = self.chat_rooms
            data['chat_accounts'] = self.chat_accounts
            
            data_file = open('chat.data', 'w')
            cPickle.dump(data, data_file)
            data_file.close()
            
        except IOError, e:
            print e
    
    def log(self, string):
        try:
            log_file = open("chat.log", 'a')
            log_file.write('\n' + string)
            log_file.close()
        except IOError, e:
            log_file = open("chat.log", 'w')
            log_file.write(string)
            log_file.close()
        
    
# Client
class Plugin(object):
    
    def __init__(self, client, server):
        ip = client.address[0]
        self.ip = ip
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
                'send' : '[{0}] {1} > {2}: {3}',
                
                'flag' : 'Flags have been set to: {0}'
                }
        
        try:
            bad_file = open("badwords.txt", "r") # Bad words list.
            badwords = bad_file.read().split("\n")
            badwords.pop()
            bad_file.close()
        except IOError:
            bad_file = open("badwords.txt", "w")
            bad_file.close()
            badwords = []
        
        try:
            good_file = open("goodwords.txt", "r") # Good words list.
            goodwords = good_file.read().split("\n")
            goodwords.pop()
            good_file.close()
        except IOError:
            good_file = open("goodwords.txt", "w")
            good_file.close()
            goodwords = []
        
        self.bad_words = badwords
        self.good_words = goodwords
        
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
        self.auth_name = ''
        
        # Add the user to the default room 'main'
        self.server.log(
            '{0} has connected with IP: {1}!'.format(self.name, ip))
        self.join_room('scratch')
    
    def broadcast(self, raw_message):
        message = raw_message.split(' ')
        request = message[0]
        args = message[1:]
        
        self.server.log(self.name + ' ' + request)
        
        if request == 'switch-room' and len(args) == 1:
            self.switch_room(args[0])
        
        elif request == 'switch-name' and len(args) == 1:
            self.switch_name(args[0])
        
        elif request == 'send' and len(args) > 0:
            self.room_message(' '.join(args))
        
        elif request == 'room' and len(args) > 0:
            self.mod_message(' '.join(args))
        
        elif request == 'me' and len(args) > 0:
            self.room_message(' '.join(args), me=1)
        
        elif request == 'auth' and len(args) == 2:
            self.auth(args[0], args[1])
        
        elif request == 'scratch-auth' and len(args) == 2:
            self.scratch_auth(args[0], args[1])
        
        elif request == 'new-account' and len(args) == 2:
            self.new_account(args[0], args[1])
        
        elif request == 'change-pass' and len(args) == 2:
            self.change_password(args[0], args[1])
        
        elif request == 'mute' and len(args) == 1:
            self.mute_user(args[0])
        
        elif request == 'force-kill' and len(args) == 1:
            self.force_kill(args[0])
        
        elif request == 'user-list' and len(args) == 0:
            self.user_list()
        
        elif request == 'guser-list' and len(args) == 0:
            self.global_user_list()
        
        elif request == 'room-list' and len(args) == 0:
            self.room_list()
        
        elif request == 'whisper' and len(args) > 1:
            self.user_message(args[0], ' '.join(args[1:]))
        
        elif request == 'flags' and len(args) == 1:
            self.set_flags(args[0])
        
        elif request == 'rank' and len(args) == 2:
            self.change_room_rank(args[0], args[1])
        
        elif request == 'grank' and len(args) == 2:
            self.change_global_rank(args[0], args[1])
        
        elif request == 'astatus' and len(args) == 1:
            self.user_status(args[0])
        
        elif request == 'set-motd' and len(args) > 0:
            self.set_motd(' '.join(args))
        
        elif request == 'update-rank' and len(args) == 0:
            self.update_rank()
        
        elif request == 'force-update' and len(args) == 1:
            self.force_update_rank(args[0])
        
        elif request == 'del-room' and len(args) == 1:
            self.delete_room(args[0])
        
        elif request == 'logout' and len(args) == 0:
            self.auth_logout()
    
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
        
        else:
            if 'flags' not in self.server.chat_rooms[new_room]:
                self.server.chat_rooms[new_room]['flags'] = '3'
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
            if self.auth_name in chat_room['ranks']:
                self.room_rank = chat_room['ranks'][self.auth_name]
            else:
                self.room_rank = self.global_rank
        else:
            self.server.chat_rooms[room] = {'ranks' :
                                                {
                                                name : '^'
                                                },
                                            'users' : [],
                                            'flags' : '3'
                                           }
            chat_room = self.server.chat_rooms[room]
            self.room_rank = chat_room['ranks'][name]
        
        chat_room['users'].append(name)
        self.room = room
        self._message_room(self.room,
                           self.messages['join'].format(name, room))
        
        if 'motd' in chat_room:
            if chat_room['motd'] != '':
                self._message_user(self.name, chat_room['motd'])
        
        else:
            chat_room['motd'] = ''
    
    def part_room(self, old_room):
        name = self.name
        old_chat_room = self.server.chat_rooms[old_room]
        if name in old_chat_room['users']:
            old_chat_room['users'].remove(name)
            
            message = self.messages['part'].format(name, old_room)
            self._message_room(old_room, message)
    
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
            
            message = self.messages['name'].format(old_name,
                                                   new_name)
            
            self._message_room(self.room, message)
    
    def scratch_auth(self, username, password):
        authed = self.scratch_authenticate(username, password)
        self.server.log(self.name + ' ' + authed)
        if authed == 'true':
            self.authenticated = True
            self.auth_name = username
            
            if username not in self.server.chat_accounts:
                self.server.chat_accounts[username] = {'rank' : '%',
                                                       'hash' : '',
                                                       'posts' : 0}
            
            self.global_rank = self.server.chat_accounts[username]['rank']
            
            message = self.messages['auth_1'].format(self.name,
                                                     username)
            self._message_user(self.name, message)
        else:
            message = self.messages['auth_0'].format(self.name,
                                                     username)
            self._message_user(self.name, message)
    
    def auth(self, username, password):
        if username in self.server.chat_accounts:
            chat_accounts = self.server.chat_accounts
            password = self.hash(password)
            
            if chat_accounts[username]['hash'] == password:
                self.authenticated = True
                self.auth_name = username
                self.global_rank = self.server.chat_accounts[username]['rank']
        
        if self.authenticated:
            message = self.messages['auth_1'].format(self.name,
                                                     username)
            self._message_user(self.name, message)
        else:
            message = self.messages['auth_0'].format(self.name,
                                                     username)
            self._message_user(self.name, message)
    
    def _auth(self, username):
        self.authenticated = True
        self.global_rank = self.server.chat_accounts[username]['rank']
    
    def change_password(self, username, password):
        if self.auth_name == username or self.global_rank in '*':
            password = self.hash(password)
            self.server.chat_accounts[username]['hash'] = password
            
            self._message_user(self.name, 'Password changed!')
    
    def new_account(self, username, password):
        password = self.hash(password)
        if username in self.server.chat_accounts:
            return
        
        chat_accounts = self.server.chat_accounts
        chat_accounts[username] = {'rank' : '+',
                                   'hash' : password,
                                   'posts' : 0}
        
        self.server.save_data()
    
    def leave(self):
        try:
            self.part_room(self.room)
                
        except Exception, e:
            self.server.log(str(e))
        
        del self.server.chat_users[self.name]
        
        self.server.log(
            '{0} has disconnected with IP: {1}!'.format(self.name,
                                                        self.ip))
    
    def room_message(self, message, me=0):
        if 'v' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*+%@^':
                pass
            else:
                return
        
        if 's' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*%@^':
                pass
            else:
                return
        
        if 'a' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*@^':
                pass
            else:
                return
        
        if '^' in self.server.chat_rooms[self.room]['flags']:
            if self.room_rank in '~*^':
                pass
            else:
                return
        
        name = self.name
        #
        #chat_room = self.server.chat_rooms[self.room]
        #if name in chat_room['ranks']:
        #    if chat_room['ranks'][name] in '#':
        #        t_rank = '#'
        
        #else:
        #    t_rank = ''
        
        if self.room_rank not in '#': # and t_rank not in '#'
            if me:
                full_message = '*' + self.room_rank
                full_message += name + ' ' + message + '*'
            
            else:
                full_message = self.room_rank
                full_message += name + ': ' + message
            
            self._message_room(self.room, full_message)
            
            if self.authenticated:
                chat_accounts = self.server.chat_accounts
                chat_accounts[self.auth_name]['posts'] += 1
    
    def user_message(self, user, message):
        censor = self.censor_message(message)
        if censor:
            message = censor
        else:
            return
        
        message = message.replace(' ', '', 1)
        
        if self.room_rank not in '#!-+':
            full_message = self.time_stamp()
            full_message += '[PM]' + self.name + ' --> ' + user + ': ' + message
            self._message_user(user, full_message)
            self._message_user(self.name, full_message)
    
    def _message_room(self, room_name, message):
        censor = self.censor_message(message)
        if censor:
            message = censor
        else:
            return
        
        message = message.replace(' ', '', 1)
        
        room = self.server.chat_rooms[room_name]['users']

        self.server.log(self.messages['send'].format(strftime("%H:%M:%S"),
                                                     self.name,
                                                     room_name,
                                                     message))
        
        message = self.time_stamp() + message
        
        for user in room:
            try:
                user = self.server.chat_users[user]
                user.send_sensor('chat', message)
                user.send_broadcast('new_message')
            except KeyError:
                room.remove(user)
    
    def _message_user(self, user, message):
        if user in self.server.chat_users:
            user = self.server.chat_users[user]
            user.send_sensor('chat', message)
            user.send_broadcast('new_message')
            
            self.server.log(self.messages['send'].format(strftime("%H:%M:%S"),
                                                         self.name,
                                                         user,
                                                         message))
    
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
            new_message = ''
            for word in message:
                for bad_word in self.bad_words:
                    if bad_word in word.lower():
                        if word.lower() not in self.good_words:
                            word = word.lower()
                            word = word.replace(bad_word, '*ponies*')
                        else:
                            word = word
                    
                    else:
                        word = word
                
                new_message += ' ' + word
            
            return new_message
        
        else:
            return raw_message
                
    def mute_user(self, name):
        if self.room_rank in '*~^@' or self.global_rank in '*~^@':
            if name in self.server.chat_rooms[self.room]['users']:
                self.server.chat_users[name].room_rank = '#'
    
    def perma_mute(self, name):
        if self.room_rank in '*~^@':
            self.server.chat_rooms[self.room]['ranks'][name] = '#'
    
    def change_room_rank(self, name, new_rank):
        if self.room_rank in '*~^@' or self.global_rank in '*~^@':
            chat_room = self.server.chat_rooms[self.room]
            if self.room_rank == '*' or self.global_rank == '*':
                chat_room['ranks'][name] = new_rank
            
            elif self.room_rank == '~' or self.global_rank == '~':
                if new_rank in '^@+!#-%':
                    chat_room['ranks'][name] = new_rank
            
            elif self.room_rank == '^' or self.global_rank == '^':
                if new_rank in '^@+!#-%':
                    chat_room['ranks'][name] = new_rank
            
            elif self.room_rank == '@' or self.global_rank == '@':
                if new_rank in '+!#-%':
                    chat_room['ranks'][name] = new_rank
            
            self.server.save_data()
    
    def change_global_rank(self, name, new_rank):
        if self.global_rank in '*':
            self.server.chat_accounts[name]['rank'] = new_rank
            
            self.server.save_data()
    
    def set_flags(self, flags):
        if (self.room_rank and self.global_rank) not in '*~^@':
            return
        
        self.server.chat_rooms[self.room]['flags'] = flags
        self._message_room(self.room,
                           self.messages['flag'].format(flags))
        
        self.server.save_data()
    
    def hash(self, hash):
        pre_salt = self.server.pre_salt
        suf_salt = self.server.suf_salt
        sec_salt = self.server.sec_salt
        
        hash = hashlib.sha512(pre_salt + hash + suf_salt)
        hash = hash.digest()
        hash = hashlib.sha256(pre_salt + hash + suf_salt)
        hash = hash.digest()
        hash = hashlib.sha512(sec_salt + hash)
        return hash.hexdigest()
    
    def force_kill(self, name):
        if self.global_rank in '*':
            if name in self.server.chat_users:
                self.server.chat_users[name].leave()
                if name in self.server.chat_users:
                    del self.server.chat_users[name]
    
    def user_list(self):
        message = ''
        for user in self.server.chat_rooms[self.room]['users']:
            message += user + ', '
        message = message[:-2] + '.'
        self._message_user(self.name, message)
    
    def global_user_list(self):
        message = ''
        for user in self.server.chat_users:
            message += user + ', '
        message = message[:-2] + '.'
        self._message_user(self.name, message)
    
    def room_list(self):
        message = ''
        for room in self.server.chat_rooms:
            message += room + ', '
        message = message[:-2] + '.'
        self._message_user(self.name, message)
    
    def update_rank(self):
        if self.auth_name in chat_room['ranks']:
                self.room_rank = self.server.chat_rooms[room]['ranks'][name]


    def scratch_authenticate(self, username, password):
        details = {'username' : username, 'password' : password}
        string = "http://scratch.mit.edu/api/authenticateuser?"
        string = string + urllib.urlencode(details)
        fp = urllib.urlopen(string)
        result = fp.read()
        fp.close()
        result = result.decode("utf8")
        if result == ' \r\nfalse':
            return 'failed'
        else:
            result = result.split(':')
            if result[2] == 'blocked':
                return 'blocked'
            else:
                return 'true'
    
    def time_stamp(self):
        return '[' + strftime('%H:%M:%S') + ']'
    
    def set_motd(self, new_motd):
        if self.room_rank in '*~@^':
            chat_room = self.server.chat_rooms[self.room]
            
            chat_room['motd'] = new_motd
            
            message = self.name + ' has change the room motd to: '
            message += new_motd
            self._room_message(self.room, message)
            
    
    def user_status(self, username):
        chat_accounts = self.server.chat_accounts
        if username in chat_accounts:
            if 'posts' not in chat_accounts[username]:
                chat_accounts[username]['posts'] = 0
            
            posts = chat_accounts[username]['posts']
            rank = chat_accounts[username]['rank']
            message = username + ' has ' + str(posts) + ' posts '
            message += 'and their rank is ' + rank + '.'
            self._message_user(self.name, message)
        
        else:
            self._message_user(self.name, 'No such user.')
    
    def update_rank(self):
        if not self.authenticated:
            return
        
        room = self.server.chat_rooms[self.room]
        chat_accounts = self.server.chat_accounts
        
        if self.auth_name in room['ranks']:
            rank = room['ranks'][self.auth_name]
            self.room_rank = rank
            self.global_rank = chat_accounts[self.auth_name]['rank']
    
    def force_update_rank(self, username):
        if self.global_rank not in '*':
            return
        
        chat_users = self.server.chat_users
        if username in chat_users:
            chat_users[username].update_rank()
    
    def mod_message(self, message):
        if self.global_rank in '*~':
            self._message_room(self.room, message)
    
    def delete_room(self, room):
        if self.global_rank in '*':
            chat_rooms = self.server.chat_rooms
            if room in chat_rooms:
                del chat_rooms[room]
                self._message_user(self.name, 'Deleted ' + room)
        
        elif self.global_rank in '~':
            chat_rooms = self.server.chat_rooms
            if room in chat_rooms:
                if self.auth_name in chat_rooms[room]['ranks']:
                    rank = chat_rooms[room]['ranks'][self.auth_name]
                    if rank in '~*^':
                        del chat_rooms[room]
                        self._message_user(self.name,
                                           'Deleted ' + room)
    
    def auth_logout(self):
        if self.authenticated:
            self.authenticated = False
            self.auth_name = ''
            self.room_rank = '-'
            self.global_rank = '-'
            self._message_user(self.name, 'You have logged out.')