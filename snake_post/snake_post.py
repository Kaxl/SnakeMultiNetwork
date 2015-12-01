#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import struct

from snake_channel import *
from timer import *

from constants import *


class SnakePost(SnakeChannel):
    def __init__(self, channel, udp=False):
        super(SnakePost, self).__init__(channel)
        self.udp = udp
        self.current_seq_number = 0  # Current seq number
        self.last_ack = 0  # Last ack number
        self.buffer_normal = list()  # List to store packets to send
        self.buffer_secure = list()  # List to store secure packets to send

        self.secure_in_network = {}
        self.ack_received = {}

        # Timers
        self.send_timer = Timer(SEND_INTERVAL, 0, True)
        self.ack_timer = Timer(ACK_INTERVAL, 0, True)

        pass

    def send(self, data, connection=(IP_SERVER, PORT_SERVER), secure=False):
        if not secure:
            self.buffer_normal.append((struct.pack('>2I', 0, 0) + data, connection))
            print "[send] Not secure : Data = ", data, " - to : ", connection
        else:
            self.buffer_secure.append((struct.pack('>2I', random.randint(1, (1 << 32) - 1), 0) + data, connection))

    def send_post(self):
        """Send a message on SnakePost layer

        This function is called periodically to send data

        Non-secure : seq_number and ack_number = 0

        Secure : seq_number != 0 and ack_number = 0

        :return:
        """
        if self.buffer_secure:
            # Send SECURE
            data, connection = self.buffer_secure[0]
            if not self.secure_in_network[connection]:

                if self.ack_received.get(connection):
                    self.ack_received[connection] = False

                self.ack_received[connection] = False
                self.secure_in_network[connection] = True

                if self.udp:  # on udp
                    self.channel.sendto(data, connection)
                else:  # on snake_channel
                    self.send_channel(data, connection)

                self.ack_timer.activate(0)

            elif self.secure_in_network[connection] and not self.ack_received[connection]:
                # RE-send SECURE
                # If we didn't received ack for secure message, resend the message
                if self.ack_timer.expired():
                    data, connection = self.buffer_secure[0]

                    if self.udp:  # on udp
                        self.channel.sendto(data, connection)
                    else:  # on snake_channel
                        self.send_channel(data, connection)
        else:
            # Send NORMAL
            data, connection = self.buffer_normal.pop(0)
            print "[send_post] Not secure : Data = ", str(data), " - to : ", connection

            if self.udp:  # on udp
                self.channel.sendto(data, connection)
            else:  # on snake_channel
                self.send_channel(data, connection)
                print "[send_post] Sent !"

    def ack(self, seq_number, connection=(IP_SERVER, PORT_SERVER)):
        pack = struct.pack('>II', 0, seq_number)

        # When sending the ack, send data with the ack, if any
        if self.buffer_normal:
            pack += self.buffer_normal.pop(0)

        if self.udp:  # on udp
            self.channel.sendto(pack, connection)
        else:  # on snake_channel
            self.send_channel(pack, connection)

    def receive_post(self):
        if self.udp:  # on udp
            data, conn = self.channel.recvfrom()
        else:  # on snake_channel
            # data, conn = self.receive_channel()
            data, conn = self.listen()

        if data is not None:
            seq_number = struct.unpack('>I', data[:4])[0]
            ack_number = struct.unpack('>I', data[:4])[0]

            # SECURE - needs ack
            if seq_number != 0 and ack_number == 0:
                self.ack(seq_number, conn)

            # If we receive an ack
            if ack_number != 0 and seq_number == 0:
                # Compare the ack_number with the current seq_number
                if ack_number == self.current_seq_number:
                    # If the ack is correct, remove the secure message from the list
                    self.buffer_secure.pop(0)
                    self.secure_in_network = False
                    self.ack_received = True
                    pass

            return data[8:]  # Return the payload

        else:
            return None
