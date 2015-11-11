#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import select
import socket
import struct

from constants import *


class SnakeChannel:
    # List of sockets
    channels = []

    def __init__(self, channel):
        self.channel = channel
        self.seq_numbers = {}
        self.clients = {}
        #self.seq_number = 0
        pass

    def send(self, data, seq=None):
        """Send data with sequence number"""
        if seq is None:  # Incrementation of sequence number (modulo)
            self.seq_number = (self.seq_number + 1) % (0x1 << 32)
        else:  # Sequence number is 0xFFFFFFFF -> connection packet
            self.seq_number = seq

        # Pack (big endian) and send message
        self.channel.sendto(struct.pack('!I%ds' % (len(data),), self.seq_number, data))

    def receive(self):
        """Receive data with sequence number"""

        # fromto -> unpack -> check seq number
        # Verification of sequence number
        data, address = self.server.recvfrom(BUFFER_SIZE)
        seq_number, payload = struct.unpack('!Is', data)

        if (self.clients[address] < seq_number or
            (seq_number < self.clients[address] and
            (self.clients[address] - seq_number) > (1 << 31))):
            return payload

        return None





        #
