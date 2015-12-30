#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from constants import *

class Player:

    def __init__(self, name, color, score, ready, positions):
        print "name : " + str(name)
        self.name = name
        print "color : " + str(color)
        self.color = color
        self.score = score
        self.ready = ready
        self.positions = positions
        self.last_update = 0

    def update_activity(self, current_time):
        self.last_update = current_time

    def timeout(self, current_time):
        #if abs(current_time - self.last_update) > Constants.TIMEOUT_PLAYER * 1000:
        #    return True
        #else:
        #    return False
        return abs(current_time - self.last_update) > Constants.TIMEOUT_PLAYER * 1000





