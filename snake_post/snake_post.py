#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import struct
import pygame
import random

from constants import *

from snake_channel.snake_channel import SnakeChannel


class SnakePost(SnakeChannel):

    def __init__(self, channel, udp=False):
        super(SnakePost, self).__init__(channel)
        self.udp = udp
        self.buffer = list() # List to store packets to send
        pass

    def send_post(self, data, connection=(IP_SERVER, PORT_SERVER), secure=False):
        """Send a message on SnakePost layer

        Non-secure : seq_number and ack_number = 0

        Secure : seq_number != 0 and ack_number = 0

        :param data:
        :param connection:
        :param secure:
        :return:
        """
        # NON secure
        if not secure:
            # Send with ack_number=0 and seq_number = 0
            seq_number = 0
            ack_number = 0
        else: # SECURE
            # If buffer is not empty, we can't send another secure message
            if not buffer:
                # Send with seq_number=random and ack_number=0
                # Waits until we receive an ack with number=random
                seq_number = random.randint(1, (1 << 32) - 1)
                ack_number = 0
                buffer.add()
            else:
                buffer.add()

        # Pack numbers and add the data
        pack = struct.pack('>II', seq_number, ack_number)
        pack += data

        if self.udp:    # on udp
            self.channel.sendto(pack, connection)
        else:           # on snake_channel
            self.send(pack, connection)

    def ack(self, seq_number, connection=(IP_SERVER, PORT_SERVER)):
        pack = struct.pack('>II', 0, seq_number)

        if self.udp:    # on udp
            self.channel.sendto(pack, connection)
        else:           # on snake_channel
            self.send(pack, connection)

    def receive_post(self):
        if self.udp:    # on udp
            data, conn = self.channel.recvfrom()
        else:           # on snake_channel
            data, conn = self.receive()

        seq_number = struct.unpack('>I', data[:4])[0]
        ack_number = struct.unpack('>I', data[:4])[0]

        # SECURE - needs ack
        if seq_number != 0 and ack_number == 0:
            self.ack(seq_number, conn)

        # If we receive an ack
        if ack_number != 0 and seq_number == 0:
            # Compare the ack_number with the current seq_number
            if ack_number == self.current_seq_number:



        return data[8:]     # Return the payload



