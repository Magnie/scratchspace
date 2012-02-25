# Authentication Plugin
# By: Magnie(http://scratch.mit.edu/users/Magnie)

# This plugin enables the use of built-in functions in the server
# that are unable to be used by default.

# A few of these features are loading, reloading, and unloading
# plugins. Which is one reason why those features aren't normally
# available.

# Server
class Server(object):
    
    def __init__(self):
        self.accounts = {} # 'username' : {'password' : 'password',
                           #               'rank' : 'rank',
                           #               'banned' : True/False}
        self.accounts['root'] = {'password' : 'root',
                                 'rank' : '!@#$%^&*()_+=-[]{}|',
                                 'banned' : False}
        self.active_users = {} # 'username' : class
    
    def login(self, username, password, _class):
        try:
            if self.accounts[username]['password'] == password:
                if self.accounts[username]['banned'] == True:
                    return False
                else:
                    self.active_users[username] = _class
                    return True
            
            else:
                return False
            
        except KeyError:
            return False
        
        return False
    
    def create_account(self, username, password, rank):
        try:
            if self.accounts[username]:
                return False
        except KeyError:
            pass
        
        self.accounts[username] = {'password' : password,
                                   'rank' : rank,
                                   'banned' : False}
        return True
    
    def delete_account(self, username):
        try:
            del self.accounts[username]
            return True
        except KeyError:
            return False
            
    def change_password(self, username, old_password, new_password):
        if self.accounts[username]['password'] == old_password:
            if self.force_change(username, new_password):
                return True
            else:
                return False
        else:
            return False
    
    def force_change(self, username, new_password):
        try:
            self.accounts[username]['password'] = new_password
            return True
        except KeyError:
            return False
    
    def add_rank(self, username, new_rank):
        try:
            current_rank = self.accounts[username]['rank']
            self.accounts[username]['rank'] = current_rank + new_rank
            return True
        except KeyError:
            return False
    
    def rem_rank(self, username, old_rank):
        try:
            current_rank = self.accounts[username]['rank']
            new_rank = current_rank.replace(old_rank, '')
            return True
        except KeyError:
            return False
    
    def load_accounts(self, filename):
        acfile = open(filename, 'r')
        self.accounts = cPickle.load(acfile)
        acfile.close()
    
    def save_accounts(self, filename):
        acfile = open(filename, 'w')
        cPickle.dump(acfile, self.accounts)
        acfile.close()

# Client
class Plugin(object):
    
    def __init__(self, client, server):
        self.client = client
        self.server = server.plugin_servers['auth']
        
        self.rank = ''
    
    def broadcast(self, original):
        message = original.split(' ')
        if self.rank in '*':
            if message[0] == '*load':
                self.client.load_plugin(message[1])
            elif message[0] == '*unload':
                self.client.unload_plugin(message[1])
        
        if message[0] == '*login':
            self.server.login(message[1], message[2], self)
    
    def disconnect(self):
        pass
        