# Author: Gustavo Hoirisch, Pieter Janssens
#
#
#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#
#

from plugin import *
import urllib2, urllib, jsonrpclib, socket, struct

class XBMC_object():
    def __init__(self, host='localhost', port='8080', username=None, password=None, mac_address=None):
        self.username = username
        self.password = password
        self.port = port
        self.host = host
        self.mac_address = mac_address
        
    def get_url(self):
        return 'http://%s@%s:%s' %(self.get_user_pass(), self.host, self.port)
        
    def get_user_pass(self):
        if self.username != None and self.password != None:
            return '%s:%s' % (self.username, self.password)
        
        return ''

class XBMC(Plugin):
    global xbmc
    xbmc = XBMC_object()
    
    @register("en-US", "(xbmc)|(xbmc.* [a-z]+)")
    def test2(self, speech, language):
        global xbmc
        command = str(speech).replace('xbmc ', '',1)
        if command != None:
            jsonrpc = jsonrpclib.Server('%s/jsonrpc' % (xbmc.get_url()))
            if command == 'stop':
                jsonrpc.Player.Stop("playerid=1")
            elif command == 'play' or command == 'pause' or command == 'plate' or command == 'place':
                jsonrpc.Player.PlayPause("playerid=1")
            elif 'play' in command or 'plate' in command or 'place' in command: #this elif needs to be located below command == 'play' part
                title = command.replace('play ', '', 1)
                result = jsonrpc.VideoLibrary.GetMovies()
                for movie in result['movies']:
                    if movie['label'].lower() == title:
                        movieid = movie['movieid']
                        jsonrpc.Player.Open("movieid="+movieid)
                #code for playing tvshows latest unwatched episode
            elif command == 'info':
                self.say("XBMC URL: %s" %(xbmc.get_url()))
            elif command == 'shut down' or command == 'shutdown' or command == 'turn off':
                self.say("XBMC going down")
        json.System.Shutdown()
        elif command == 'boot' or command == 'start' or command == 'boot up':
            addr_byte = xbmc.mac_address.split(':')
            hw_addr = struct.pack('BBBBBB',
            int(addr_byte[0], 16),
            int(addr_byte[1], 16),
            int(addr_byte[2], 16),
            int(addr_byte[3], 16),
            int(addr_byte[4], 16),
            int(addr_byte[5], 16))
            msg = '\xff' * 6 + hw_addr * 16
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            s.sendto(msg, ("255.255.255.255", 9))
        else:
                self.say("XBMC command not recognized: %s."%(command))

        else:
            self.say("XBMC currently supports the following commands: play, pause, stop and info.")
        
        self.complete_request()