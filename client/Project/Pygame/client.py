#! /usr/bin/env pythonprint "Importing threading, socket, and json."import threadingimport socketimport jsonprint "Importing array and re."from array import arrayimport reprint "Importing soulite."import souliteclass Connection(threading.Thread):    def __init__(self):        threading.Thread.__init__(self)        def open_socket(self, host, port):        self.sock = socket.socket( ) # Define the socket type.        self.sock.connect((host, port)) # Connects to the Host/Server IP Address.        self.size = 1024        def send(self, message):        message = self.sendScratchCommand(message)        self.sock.send(message)        def run(self):        alive = 1        while alive:            try:                data = self.sock.recv(SIZE)                print data                data = self.parse_message(data)                print data            except Exception, e:                print e                alive = 0                continue                        # For every broadcast, do_broadcast('broadcast')            for broadcast in data['broadcast']:                self.do_broadcast( broadcast )                            # For every sensor-update, do_sensor('sensor', 'value')            for sensor in data['sensor-update']:                self.do_sensor( sensor, data['sensor-update'][sensor] )                def do_sensor(self, name, value):        if name == 'pid':            player.player_id = value        elif name[0] == 'p':            pid = name[1:-1]            type = name[-1]                        player.players[pid][type] = int(value)        def do_broadcast(self, message):        pass            def sendScratchCommand(self, cmd):        # I was never sure what this did, but it's required.        n = len(cmd)        a = array('c')        a.append(chr((n >> 24) & 0xFF))        a.append(chr((n >> 16) & 0xFF))        a.append(chr((n >>  8) & 0xFF))        a.append(chr(n & 0xFF))        return (a.tostring() + cmd)        def parse_message(self, message):        #TODO: parse sensorupdates with quotes in sensor names and values        #	   make more readable        if message:            sensorupdate_re = 'sensor-update[ ](((?:\").[^\"]*(?:\"))[ ](?:\"|)(.[^\"]*)(?:\"|)[ ])+'            broadcast_re = 'broadcast[ ]\".[^"]*\"'            sensors = {}            broadcast = []            sensorupdates = re.search(sensorupdate_re, message)            if sensorupdates:                            # formats string to '<sensor> <value> <sensor1> <value1> ...'                sensorupdates = sensorupdates.group()                sensorupdates = sensorupdates.replace('sensor-update', '')                sensorupdates = sensorupdates.strip().split()                                # for sensors that are multiple words, make sure that entire                # sensor name shows up as one sensor value in the list                i = 0                sensorlist = []                while i < len(sensorupdates):                    if sensorupdates[i][0] == '\"':                        if sensorupdates[i][-1] != '\"':                            j = i                            multisense = ''                            #now loop through each word in list and find the word                             #that ends with " which is the end of the variable name                            while j < len(sensorupdates):                                multisense = multisense+' '+sensorupdates[j]                                if sensorupdates[j][-1] == '\"':                                    break                                i+=1                                j+=1                            sensorlist.append(multisense.strip(' \"'))                        else:                            sensorlist.append(sensorupdates[i].strip(' \"'))                    else:                        sensorlist.append(sensorupdates[i])                    i+=1			                i = 0                # place sensor name and values in a dictionary                while len(sensors) < len(sensorlist)/2:                    sensors[sensorlist[i]] = sensorlist[i+1]                    i+=2            broadcasts = re.findall(broadcast_re, message)            if broadcasts:                # strip each broadcast message of quotes ("") and "broadcast"                broadcast = [mess.replace('broadcast','').strip('\" ') for mess in broadcasts]		            return dict([('sensor-update', sensors), ('broadcast', broadcast)])        else:             return Noneclass Ship(soulite.Sprite):        def __init__(self):        soulite.Sprite.__init__(self, vs_project, name="ship")                self.max_players = 12                self.players = {}        for player in xrange(0, self.max_players):            self.players[str(player)] = {'x' : 0, 'y' : 0, 'd' : 0}                self.player_id = '0'                self.add_costume(costume_file='Ship1.gif', path='image', colorkey=0x000000)        self.set_costume('Ship1.gif')                self.up = 0        self.right = 0        self.left = 0        def update(self):        xpos = self.players[self.player_id]['x']        ypos = self.players[self.player_id]['y']        angle = self.players[self.player_id]['d']                for player_id in self.players:            if player_id == self.player_id:                self.go_to(256, 256)                self.set_direction(angle)                self.stamp()            else:                x = self.players[player_id]['x'] # X pos                y = self.players[player_id]['y'] # Y pos                d = self.players[player_id]['d'] # Direction                                temp_x = (x - xpos) + 256                temp_y = (x - ypos) + 256                self.go_to(temp_x, temp_y)                self.set_direction(d)                self.stamp()                up = self.up        right = self.right        left = self.left                if self.key_pressed('K_UP'):            if not up:                con.send('broadcast ":forward-true"')                up = 1        else:            if up:                con.send('broadcast ":forward-false"')                up = 0                    if self.key_pressed('K_LEFT'):            if not left:                con.send('broadcast ":left-true"')                left = 1        else:            if left:                con.send('broadcast ":left-false"')                left = 0                if self.key_pressed('K_RIGHT'):            if not right:                con.send('broadcast ":right-true"')                right = 1        else:            if right:                con.send('broadcast ":right-false"')                right = 0                self.up = up        self.right = right        self.left = leftvs_project = soulite.Project()player = Ship()HOST = '127.0.0.1' # Host/Server IP Address for connecting.PORT = 54001       # The port the server uses.SIZE = 1024con = Connection()con.open_socket(HOST, PORT)con.start()con.send('broadcast "<virtual_space"')con.send('broadcast ":player-id"')raw_input()while True:    con.send('broadcast ":update"')        print "Updating sprites."    vs_project.tick(10)    vs_project.update_all()