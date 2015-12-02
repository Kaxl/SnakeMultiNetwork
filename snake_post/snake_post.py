#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import struct

from snake_channel import *
from timer import *

from constants import *


class SnakePost(SnakeChannel):
    """SnakePost class

    """
    def __init__(self, channel, udp=False):
        super(SnakePost, self).__init__(channel)
        self.udp = udp
        # Key of dictionary is the connection, value is a list of packets to send
        self.buffer_normal = {}  # Dict to store packets to send
        self.buffer_secure = {}  # Dict to store secure packets to send

        self.last_ack = {}  # Last ack number
        self.last_seq_number = {}  # Last seq number
        self.secure_in_network = {}
        self.ack_received = {}

        # Timers
        self.ack_timer = Timer(ACK_INTERVAL, 0, True)

    def listen(self):
        """Listen for incoming messages (server)
        if the connection is not done, handle the connection (snake channel)
        :return:
        """
        data, conn = self.listen_channel()
        self.init_dict(conn)
        # If we receive some data, the client is already connected
        if data is not None and conn is not None:
            payload = self.process_data(data, conn)
            return payload
        else:
            return None

    def init_dict(self, connection):
        """Initialization of dictionnaries

        :param connection: Connection to init
        :return:
        """
        if not self.buffer_normal.get(connection):
            self.buffer_normal[connection] = []
        if not self.buffer_secure.get(connection):
            self.buffer_secure[connection] = []
        if not self.last_ack.get(connection):
            self.last_ack[connection] = None
        if not self.last_seq_number.get(connection):
            self.last_seq_number[connection] = None
        if not self.ack_received.get(connection):
            self.ack_received[connection] = None
        if not self.secure_in_network.get(connection):
            self.secure_in_network[connection] = None

    def is_connected(self, connection):
        """Check if client is connected

        :param connection: client to test
        :return:
        """
        return self.connections[connection][D_STATUS]

    def send(self, data, connection=(IP_SERVER, PORT_SERVER), secure=False):
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
            self.buffer_normal[connection].append((struct.pack('>2I', 0, 0) + data, connection))
            #print "[send] Not secure : Data = ", data, " - to : ", connection
        else:
            self.buffer_secure[connection].append((struct.pack('>2I', random.randint(1, (1 << 32) - 1), 0) + data, connection))

    def process_buffer(self):
        """Check buffer from each connection and send a message

        Secure message have the highest priority

        If the timer for the ack is expired, we resend the previous secure message
        The last secure message is not pop yet, we wait for the ack

        :return:
        """
        for connection in self.connections:
            if self.secure_in_network.get(connection) and \
                    self.secure_in_network[connection] and \
                    not self.ack_received[connection] and \
                    self.ack_timer.expired(pygame.time.Clock()):
                # RE-send SECURE
                # If we didn't received ack for secure message, resend the message
                data = self.buffer_secure[connection][0]

                if self.udp:  # on udp
                    self.channel.sendto(data, connection)
                else:  # on snake_channel
                    self.send_channel(data, connection)

            elif self.buffer_secure.get(connection) and \
                    self.buffer_secure[connection] and \
                    not self.secure_in_network[connection]:
                # Send SECURE
                # Get the first secure packet to send
                # We don't pop it because we will wait for the ack
                data = self.buffer_secure[connection][0][0]
                if not self.secure_in_network[connection]:
                    # We are sending a secure message, we need to receive a ack and
                    # we can't have two secure message at the same time on the same channel
                    self.ack_received[connection] = False
                    self.secure_in_network[connection] = True

                    if self.udp:  # on udp
                        self.channel.sendto(data, connection)
                    else:  # on snake_channel
                        self.send_channel(data, connection)

                    # Activate the timer in order to resend the message if it expires
                    self.ack_timer.activate(0)

            else:
                # Send NORMAL
                if self.buffer_normal.get(connection) and \
                        self.buffer_normal[connection]:
                    data = self.buffer_normal[connection].pop(0)[0]
                    #print "[send_post] Not secure : Data = ", str(data), " - to : ", connection

                    if self.udp:  # on udp
                        self.channel.sendto(data, connection)
                    else:  # on snake_channel
                        self.send_channel(data, connection)
                        #print "[send_post] Sent !"

    def ack(self, seq_number, connection=(IP_SERVER, PORT_SERVER)):
        """Send an ack

        :param seq_number: sequence number
        :param connection: destination
        :return:
        """
        pack = struct.pack('>II', 0, seq_number)

        # When sending the ack, send data with the ack, if any
        if self.buffer_normal[connection]:
            pack += self.buffer_normal[connection].pop(0)

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
        if data is not None:
            seq_number = struct.unpack('>I', data[:4])[0]
            ack_number = struct.unpack('>I', data[4:8])[0]

            # SECURE - needs ack
            if seq_number != 0 and ack_number == 0:
                self.ack(seq_number, conn)

            # If we receive an ack
            if ack_number != 0 and seq_number == 0:
                # Compare the ack_number with the last seq_number
                if ack_number == self.last_seq_number[conn]:
                    # If the ack is correct, remove the secure message from the list
                    self.buffer_secure[conn].pop(0)
                    self.secure_in_network[conn] = False
                    self.ack_received[conn] = True
                    pass

            return data[8:]  # Return the payload
        else:
            return None

    def receive(self):
        """Receive messages (client part)

        :return:
        """
        #print "receive post init"
        if self.udp:  # on udp
            data, conn = self.channel.recvfrom(BUFFER_SIZE)
        else:  # on snake_channel
            #print "on snake channel"
            data, conn = self.receive_channel()

        self.init_dict(conn)
        return self.process_data(data, conn)
