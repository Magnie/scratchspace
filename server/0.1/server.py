#!/usr/bin/env python 

""" 
An echo server that uses threads to handle multiple clients at a time. 
Entering any line of input at the terminal will exit the server. 
""" 

from array import array
import select 
import socket 
import sys 
import threading 
import json
import re

class Server: 
    def __init__(self): 
        self.host = '' 
        self.port = int( raw_input("Port: ") )
        self.backlog = 5 
        self.size = 1024 
        self.server = None 
        self.threads = [] 
        
        # List of plugins to import.
        self.plugins = ['test', 'virtual_space']
        
        # This is used for the "servers" of the plugins
        # for clients to communicate data with.
        self.plugin_servers = {}
        
        # This goes through all the plugins and creates
        # creates the "servers" for them.
        for plugin in self.plugins:
            exec( 'from plugins.'+plugin+' import Server' )
            exec( 'self.plugin_servers["'+plugin+'"] = Server()' )
        print self.plugin_servers

    def open_socket(self): 
        try: 
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            self.server.bind((self.host,self.port)) 
            self.server.listen(5) 
        except socket.error, (value,message): 
            if self.server: 
                self.server.close() 
            print "Could not open socket: " + message 
            sys.exit(1) 

    def run(self):
        self.open_socket() # Open a socket so people can connect.
        running = 1
        id = 0 # To define each client.
        while running:
            id += 1 # Increase so no client has the same ID.
            c = Client(self.server.accept()) # Waits for a client then accepts it.
            print c.address[0], 'has connected.'
            c.start() # Starts it.
            self.threads.append(c) # Adds it to a list so the variable c and be used for the next client.

        # Disconnect all clients.
        self.server.close() # Disconnect socket.
        for c in self.threads: # For each thread
            c.join() # End that thread.

class Client(threading.Thread): 
    def __init__(self,(client,address)): 
        threading.Thread.__init__(self) 
        self.client = client 
        self.address = address 
        self.size = 1024 
        self.plugins = {}

    def run(self): 
        running = 1 
        while running: 
            try:
                data = self.client.recv(self.size)
                data = self.parse_message(data)
            except:
                data = ''
            
            print data
            if data:
                # For every broadcast, do_broadcast('broadcast')
                for broadcast in data['broadcast']:
                    self.do_broadcast( broadcast )
                
                # For every sensor-update, do_sensor('sensor', 'value')
                for sensor in data['sensor-update']:
                    self.do_sensor( sensor, data['sensor-update'][sensor] )
            else:
                for plugin in self.plugins:
                    try:
                        self.plugins[plugin].disconnect()
                    except Exception, error:
                        print str( error )
                        pass
                del self.plugins
                print self.address[0], 'has disconnected.'
                self.client.close()
                running = 0
    
    def parse_message(self, message):
        #TODO: parse sensorupdates with quotes in sensor names and values
        #	   make more readable

        if message:
            sensorupdate_re = 'sensor-update[ ](((?:\").[^\"]*(?:\"))[ ](?:\"|)(.[^\"]*)(?:\"|)[ ])+'
            broadcast_re = 'broadcast[ ]\".[^"]*\"'
            sensors = {}
            broadcast = []

            sensorupdates = re.search(sensorupdate_re, message)
            if sensorupdates:
            
                # formats string to '<sensor> <value> <sensor1> <value1> ...'
                sensorupdates = sensorupdates.group()
                sensorupdates = sensorupdates.replace('sensor-update', '')
                sensorupdates = sensorupdates.strip().split()
                
                # for sensors that are multiple words, make sure that entire
                # sensor name shows up as one sensor value in the list
                i = 0
                sensorlist = []
                while i < len(sensorupdates):
                    if sensorupdates[i][0] == '\"':
                        if sensorupdates[i][-1] != '\"':
                            j = i
                            multisense = ''
                            #now loop through each word in list and find the word 
                            #that ends with " which is the end of the variable name
                            while j < len(sensorupdates):
                                multisense = multisense+' '+sensorupdates[j]
                                if sensorupdates[j][-1] == '\"':
                                    break
                                i+=1
                                j+=1
                            sensorlist.append(multisense.strip(' \"'))
                        else:
                            sensorlist.append(sensorupdates[i].strip(' \"'))
                    else:
                        sensorlist.append(sensorupdates[i])
                    i+=1			
                i = 0
                # place sensor name and values in a dictionary
                while len(sensors) < len(sensorlist)/2:
                    sensors[sensorlist[i]] = sensorlist[i+1]
                    i+=2

            broadcasts = re.findall(broadcast_re, message)
            if broadcasts:
                # strip each broadcast message of quotes ("") and "broadcast"
                broadcast = [mess.replace('broadcast','').strip('\" ') for mess in broadcasts]
		
            return dict([('sensor-update', sensors), ('broadcast', broadcast)])
        else: 
            return None
    
    def load_plugin(self, plugin): # Load plugin into server plugins
        if plugin not in s.plugins:
            s.plugins.append( plugin )
            try:
                reload( plugin )
            except NameError:
                exec( 'import '+plugin )
        
    
    def unload_plugin(self, plugin): # Unload plugin from server plugins
        if plugin in s.plugins:
            del s.plugins[ plugin ]
            #exec( 'del '+plugin )
    
    def reload_all_plugins(self):
        for plugin in s.plugins:
            exec( 'from plugins.'+plugin+' import Server' )
            exec( 'self.plugin_servers["'+plugin+'"] = Server()' )
    
    def use_plugin(self, plugin): # Add plugin to client
        if plugin in s.plugins: # If it exists
            if plugin in self.plugins:
                self.plugins[plugin].disconnect()
                del self.plugins[plugin]
            try:
                exec( 'reload( '+plugin+' )' )
            except NameError or Exception, e:
                print e
                s.plugins.append( plugin ) # Add it
            
                exec( 'from plugins import '+plugin)
            exec('self.plugins[plugin] = '+plugin+'.Plugin(self, s)')
            return 'Added plugin.'
        else: # Else, do nothing
            return 'No such plugin.'
    
    def not_plugin(self, plugin): 
        # Removes a plugin from the plugin list that the client uses.
        if plugin in self.plugins:
            del self.plugins[ plugin ]
            return 'Plugin removed.'
        else:
            return 'No such plugin.'
    
    def do_broadcast(self, broadcast):
        if broadcast: 
            if broadcast[0] == '<': # Use plugin
                self.use_plugin( broadcast[1:] )
            elif broadcast[0] == '>': # Stop using plugin
                self.not_plugin( broadcast[1:] )
            elif broadcast[0] == '|': # Echo broadcast
                self.send_broadcast( broadcast[1:] )
            elif broadcast[0] == ':': # Send to a plugin
                for plugin in self.plugins:
                    try:
                        self.plugins[plugin].broadcast(broadcast[1:])
                    except Exception, error:
                        print str( error )
                        pass
        else: 
            self.client.close()
            return False
        return True
    
    def do_sensor(self, name, value):
        return True

    def send_broadcast(self, value):
        broadcast = self.sendScratchCommand('broadcast "'+value+'"')
        self.client.send( broadcast )
    
    def send_sensor(self, name, value):
        sensor = self.sendScratchCommand(
                                        'sensor-update "'+name+'" "'+value+'"'
                                        )
        self.client.send( sensor )
        
    def sendScratchCommand(self, cmd):
        # I was never sure what this did, but it's required.
        n = len(cmd)
        a = array('c')
        a.append(chr((n >> 24) & 0xFF))
        a.append(chr((n >> 16) & 0xFF))
        a.append(chr((n >>  8) & 0xFF))
        a.append(chr(n & 0xFF))
        return (a.tostring() + cmd)

if __name__ == "__main__": 
    s = Server() 
    s.run()