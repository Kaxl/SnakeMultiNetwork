#!/usr/bin/python2.7
# -*- coding: utf-8 -*-


import pygame


class Timer(object):
    """
    Timer
    """

    def __init__(self, timeout, init_time, func):
        self.timeout = timeout
        self.init_time = init_time
        self.func = func
        self.active = True

    def activate(self, current_time):
        self.init_time = current_time
        self.active = True

    def check_timeout(self, current_time):
        if self.active:
            if (current_time - self.init_time) > self.timeout:
                self.func()
                self.active = False
                return True
        return False


def print1():
    print "TIMEOUT 1"


def print2():
    print "TIMEOUT 2"

if __name__ == "__main__":
    pygame.init()

    clock = pygame.time.Clock()
    curr_time = 0

    t1 = Timer(1000, 0, print1)
    t2 = Timer(3000, 0, print2)

    while True:
        curr_time += clock.tick(100)

        if t1.check_timeout(curr_time):
            t1.activate(curr_time)
        if t2.check_timeout(curr_time):
            t2.activate(curr_time)
