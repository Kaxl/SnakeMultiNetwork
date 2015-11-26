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
        self.buffer_normal = list() # List to store packets to send
        self.buffer_secure = list() # List to store secure packets to send
        pass

    def send(self, data, connection=(IP_SERVER, PORT_SERVER), secure=False):
        if not secure:
            self.buffer_normal.append((struct.pack('>2I', 0, 0) + data, connection))
        else:
            self.buffer_secure.append((struct.pack('>2I', random.randint(1, (1 << 32) - 1), 0) + data, connection))

    def send_post(self, connection=(IP_SERVER, PORT_SERVER)):
        """Send a message on SnakePost layer

        Non-secure : seq_number and ack_number = 0

        Secure : seq_number != 0 and ack_number = 0

        :param connection:
        :return:
        """
        if not self.buffer_secure:
            if self.udp:    # on udp
                self.channel.sendto(self.buffer_secure.pop(0), connection)
            else:           # on snake_channel
                self.send_channel(self.buffer_secure.pop(0), connection)
        else:
            if self.udp:    # on udp
                self.channel.sendto(self.buffer_normal.pop(0), connection)
            else:           # on snake_channel
                self.send_channel(self.buffer_normal.pop(0), connection)
                # si pas de data dnas le secure, prendre data normal
                # tant qu'on a pas recu d'ack, renvoyer message toutes les 30 ms

    def ack(self, seq_number, connection=(IP_SERVER, PORT_SERVER)):
        pack = struct.pack('>II', 0, seq_number)

        if self.udp:    # on udp
            self.channel.sendto(pack, connection)
        else:           # on snake_channel
            self.send_channel(pack, connection)

    def receive_post(self):
        if self.udp:    # on udp
            data, conn = self.channel.recvfrom()
        else:           # on snake_channel
            data, conn = self.receive_channel()

        seq_number = struct.unpack('>I', data[:4])[0]
        ack_number = struct.unpack('>I', data[:4])[0]

        # SECURE - needs ack
        if seq_number != 0 and ack_number == 0:
            self.ack(seq_number, conn)

        # If we receive an ack
        if ack_number != 0 and seq_number == 0:
            # Compare the ack_number with the current seq_number
            if ack_number == self.current_seq_number:
                pass


        return data[8:]     # Return the payload



