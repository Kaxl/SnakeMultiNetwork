#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import struct
import pygame

from constants import *

from snake_channel.snake_channel import SnakeChannel


class SnakePost(SnakeChannel):

    def __init__(self, channel, udp=False):
        super(SnakePost, self).__init__(channel)
        self.udp = udp
        self.buffer = list() # List to store packets to send
        pass

    def send_post(self, data, connection=(IP_SERVER, PORT_SERVER), ack=False):
        if self.udp:    # on udp
            print("UDP")
            self.channel.sendto()
        else:           # on snake_channel
            print("Snake channel")

    def receive_post(self):
        if self.udp:    # on udp
            print("UDP")
            self.channel.recvfrom()
        else:           # on snake_channel
            print("Snake channel")


