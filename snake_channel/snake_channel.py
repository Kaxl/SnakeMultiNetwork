#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import select
import socket
import struct

from constants import *


class SnakeChannel(object):

    def __init__(self, channel):
        self.channel = channel
        self.connections = {}
        pass

    def send(self, data, connection, seq=None):
        """Send data with sequence number"""
        if seq is None:  # Incrementation of sequence number (modulo)
            self.connections[connection] = (self.connections[connection] + 1) % (0x1 << 32)
        else:  # Sequence number is 0xFFFFFFFF -> connection packet
            self.connections[connection] = seq

        # Pack (big endian) and send message
        self.channel.sendto(struct.pack('!I%ds' % (len(data),), self.connections[connection], data), connection)

    def receive(self):
        """Receive data with sequence number"""
        # fromto -> unpack -> check seq number
        # Verification of sequence number
        data, address = self.channel.recvfrom(BUFFER_SIZE)
        seq_number, payload = struct.unpack('!Is', data)

        if (self.connections[address] < seq_number or
            (seq_number < self.connections[address] and
            (self.connections[address] - seq_number) > (1 << 31))):
            return payload, address

        return None





        #
