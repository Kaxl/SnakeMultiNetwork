#
#  YetAnotherPythonSnake 0.92
#  Author: Simone Cingano (simonecingano@gmail.com)
#  Web: http://simonecingano.it
#  Licence: MIT
#

import argparse
import getpass
import pickle
#YASP common imports
from constants import Constants


class Preferences(object):
    def __init__(self):
        self.preferences = {}
        self.fullscreen=False
        sysusername = getpass.getuser() 
        # default preferences [first run or missing file]
        self.default = {"nickname":sysusername,"color":"green","server":"127.0.0.1","port":1234}
        
	self.filename = Constants.PREFERENCES_FILE
        
        #first load existing preference
        #if the preference file do not exist, 
        #use the default defined earlier
        self.load()
        
        #after that, modify them according to flags
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-n","--nickname",type=str,help="Choose nickname")
        self.parser.add_argument("-f","--fullscreen",help="fullscreen mode", action="store_true")
        self.parser.add_argument("-c","--color",type=str,help="snake's color")
        self.parser.add_argument("-s","--server",type=str,help="snake's server IP address")
        self.parser.add_argument("-p","--port",type=int,help="snake's server port number")
        self.args = self.parser.parse_args()
        if self.args.server:
                self.preferences["server"]=self.args.server
        if self.args.port:
                self.preferences["port"]=self.args.port
        if self.args.color:
                self.preferences["color"]=self.args.color
        if self.args.nickname:
                self.preferences["nickname"]=self.args.nickname
        
        #full screen is never saved
        if self.args.fullscreen:
                self.fullscreen=True
        
        self.save()

    def get(self,key):
        return self.preferences.get(key,None)

    def set(self,key,value):
        self.preferences[key] = value

    def load(self):
        pref_file = None
        try:
            pref_file = open(self.filename,"rb")
            self.preferences = pickle.load(pref_file)
        except:
            self.preferences = self.default
        finally:
            if pref_file: pref_file.close()

    def save(self):
        self.set("fullscreen",False) 
        
        pref_file = None
        try:
            pref_file = open(self.filename,"wb")
            pickle.dump(self.preferences,pref_file)
        except:
            pass
        finally:
            if pref_file: pref_file.close()
