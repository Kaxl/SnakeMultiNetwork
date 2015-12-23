#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from constants import *

class Player:

    def __init__(self, name, color, score, ready, positions):
        self.name = name
        self.color = color
        self.score = score
        self.ready = ready
        self.positions = positions
        self.last_update = ''

    def update_activity(self, current_time):
        self.last_update = current_time

    def timeout(self, current_time):
        return abs(current_time - self.last_update) > Constants.TIMEOUT_PLAYER * 1000





