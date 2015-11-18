#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import struct
import pygame

from constants import *

from snake_channel.snake_channel import SnakeChannel


class SnakePost(SnakeChannel):

    def __init__(self, channel):
        super(SnakePost, self).__init__(channel)
        pass


