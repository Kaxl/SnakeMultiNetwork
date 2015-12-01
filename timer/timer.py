#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


import pygame


class Timer(object):
    """
    Timer
    """

    def __init__(self, timeout, init_time, periodic=False):
        self.timeout = timeout
        self.init_time = init_time
        self.active = True
        self.periodic = periodic    # Function is called periodically

    def activate(self, current_time):
        self.init_time = current_time
        self.active = True

    def expired(self, current_time):
        if self.active:
            if (current_time - self.init_time) > self.timeout:
                if self.periodic:
                    self.activate(current_time)
                else:
                    self.active = False
                return True
        return False
