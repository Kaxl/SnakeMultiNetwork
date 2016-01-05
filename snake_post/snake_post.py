#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys

sys.path.append('..')

from snake_channel import *
from timer import *
from constants import *
import pygame


class SnakePost(SnakeChannel):
    """SnakePost class
    """

    def __init__(self, channel, ip, port, color='', nickname='', udp=False):
        super(SnakePost, self).__init__(channel, ip, port, color, nickname)
        self.udp = udp
        # Key of dictionary is the connection, value is a list of packets to send
        self.buffer_normal = {}  # Dict to store packets to send
        self.buffer_secure = {}  # Dict to store secure packets to send

        self.last_ack = {}  # Last ack number
        self.last_seq_number = {}  # Last seq number
        self.secure_in_network = {}
        self.ack_received = {}

        # Timers
        self.ack_timer_dict = {}

        self.clock = pygame.time.Clock()
        self.current_time = 0

    def listen(self):
        """Listen for incoming messages (server)
        if the connection is not done, handle the connection (snake channel)
        In udp, you can juste use the receive method because there is no connection on the server side
        :return:
        """
        data, conn = self.listen_channel()

        self.init_dict(conn)
        # If we receive some data, the client is already connected
        if data is not None and conn is not None:
            payload, conn = self.process_data(data, conn)
            return payload, conn
        else:
            return None, None

    def init_dict(self, connection):
        """Initialization of dictionaries

        :param connection: Connection to init
        :return:
        """
        if not self.buffer_normal.get(connection):
            self.buffer_normal[connection] = []
        else:
            return
        if not self.buffer_secure.get(connection):
            self.buffer_secure[connection] = []
        if not self.last_ack.get(connection):
            self.last_ack[connection] = None
        if not self.last_seq_number.get(connection):
            self.last_seq_number[connection] = []
        if not self.ack_received.get(connection):
            self.ack_received[connection] = []
        if not self.secure_in_network.get(connection):
            self.secure_in_network[connection] = []
        if not self.ack_timer_dict.get(connection):
            self.ack_timer_dict[connection] = Timer(ACK_INTERVAL, 0, True)

    def is_connected(self, connection):
        """Check if client is connected

        :param connection: client to test
        :return:
        """
        return self.connections[connection][D_STATUS]

    def send(self, data, connection, secure=False):
        """Add the data into the dictionary (the key is the connection)

        The header of snake post is add (seq_number and ack_number)

        Non-secure : seq_number and ack_number = 0

        Secure : seq_number != 0 and ack_number = 0

        :param data: data to send
        :param connection: destination
        :param secure: secure or not
        :return:
        """
        self.init_dict(connection)
        if not secure:
            self.buffer_normal[connection].append((struct.pack('>2H', 0, 0) + data, connection))
        else:
            if len(self.buffer_secure[connection]) < MAX_SIZE_LIST:
                self.last_seq_number[connection].append(random.randint(1, (1 << 16) - 1))
                self.buffer_secure[connection].append(
                    (struct.pack('>2H', self.last_seq_number[connection][-1], 0) + data, connection))
            else:
                print "Buffer secure is full, try again later."

    def process_buffer(self):
        """Check buffer from each connection and send a message

        Secure message have the highest priority

        If the timer for the ack is expired, we resend the previous secure message
        The last secure message is not pop yet, we wait for the ack

        :return:
        """
        self.current_time += self.clock.tick(FPS)
        for connection in self.connections:
            if self.secure_in_network.get(connection) and \
                    not self.ack_received.get(connection) and \
                    self.ack_timer_dict.get(connection).expired(self.current_time):
                # RE-send SECURE
                # If we didn't received ack for secure message, resend the message
                data = self.buffer_secure[connection][0][0]

                if self.udp:  # on udp
                    self.channel.sendto(data, connection)
                else:  # on snake_channel
                    self.send_channel(data, connection)

            elif self.buffer_secure.get(connection) and \
                    not self.secure_in_network.get(connection):
                # Send SECURE
                # Get the first secure packet to send
                # We don't pop it because we will wait for the ack
                data = self.buffer_secure[connection][0][0]

                # We are sending a secure message, we need to receive a ack and
                # we can't have two secure message at the same time on the same channel
                self.ack_received[connection] = False
                self.secure_in_network[connection] = True

                if self.udp:  # on udp
                    self.channel.sendto(data, connection)
                else:  # on snake_channel
                    self.send_channel(data, connection)

                # Activate the timer in order to resend the message if it expires
                self.ack_timer_dict[connection].activate(self.current_time)
            else:
                # Send NORMAL
                if self.buffer_normal.get(connection):
                    data = self.buffer_normal.get(connection).pop(0)[0]

                    if self.udp:  # on udp
                        self.channel.sendto(data, connection)
                    else:  # on snake_channel
                        self.send_channel(data, connection)

    def ack(self, seq_number, connection):
        """Send an ack

        :param seq_number: sequence number
        :param connection: destination
        :return:
        """
        pack = struct.pack('>2H', 0, seq_number)
        # When sending the ack, send data with the ack, if any
        if self.buffer_secure.get(connection) and \
                not self.secure_in_network.get(connection):
            # Secure message
            # Set a random seq_number
            pack = struct.pack('>2H', self.last_seq_number[connection][0], seq_number)
            pack += self.buffer_secure[connection][0][0]
            self.secure_in_network[connection] = True
            self.ack_received[connection] = False
        elif self.buffer_normal.get(connection):
            # Normal message
            pack += self.buffer_normal[connection].pop(0)[0]

        if self.udp:  # on udp
            self.channel.sendto(pack, connection)
        else:  # on snake_channel
            self.send_channel(pack, connection)

    def process_data(self, data, conn):
        """Process the data we receive
        Check the seq_number and ack_number

        If this is a secure message, we send an ack.
        If we receive an ack, we compare it with the last seq_number
        :param data: data received
        :param conn: sender
        :return:
        """
        if data is not None and len(data) >= 4:
            seq_number = struct.unpack('>H', data[:2])[0]
            ack_number = struct.unpack('>H', data[2:4])[0]

            # SECURE - needs ack
            if seq_number != 0:
                self.ack(seq_number, conn)

            # If we receive an ack
            if ack_number != 0 and len(self.last_seq_number[conn]) > 0:
                # Compare the ack_number with the last seq_number
                if ack_number == self.last_seq_number[conn][0]:
                    # If the ack is correct, remove the secure message from the list
                    self.buffer_secure[conn].pop(0)
                    self.last_seq_number[conn].pop(0)
                    self.secure_in_network[conn] = False
                    self.ack_received[conn] = True
                    #if seq_number != 0:
                    #    self.ack(seq_number, conn)
                else:
                    if self.udp:  # on udp
                        self.channel.sendto(self.buffer_secure[conn][0][0], conn)
                    else:  # on snake_channel
                        self.send_channel(self.buffer_secure[conn][0][0], conn)

            if len(data[4:]) == 0:
                return None, None
            else:
                return data[4:], conn  # Return the payload
        else:
            return None, None

    def receive(self):
        """Receive messages (client part)

        :return:
        """
        if self.udp:  # on udp
            try:
                data, conn = self.channel.recvfrom(BUFFER_SIZE)
            except socket.error:
                return None, None
        else:  # on snake_channel
            data, conn = self.receive_channel()

        self.init_dict(conn)
        return self.process_data(data, conn)
