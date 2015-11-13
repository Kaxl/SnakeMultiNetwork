#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import json
from constants import *


class SnakeChannel(object):
    """Class SnakeChannel

    Handle the send and receive of messages protocol.
    This class is inherited by Client and Server class to send and receive message.
    It contains a channel (socket) and a dictionary of connections :
    key : (ip, port)
    value : sequence number

    TODO : Do we need to have the B value for security issues ? (crypt / decrypt)
    """
    def __init__(self, channel):
        """Initialization of SnakeChannel

        :param channel: Socket for the connection
        :return:
        """
        self.channel = channel
        self.connections = {}
        pass

    def send(self, data, connection, seq=None):
        """Send data with sequence number

        If a sequence number is provided and is 0xffffffff, then this
        is an outbound message and we process it.
        Else, we increment the sequence number.

        :param data: data to send
        :param connection: connection (ip, port)
        :param seq: sequence number if provided
        """
        if seq is None:  # Incrementation of sequence number (modulo)
            self.connections[connection] = (self.connections[connection] + 1) % (0x1 << 32)
        else:  # Sequence number is 0xFFFFFFFF -> connection packet
            self.connections[connection] = seq

        # Send the message in json format
        self.channel.sendto(json.dumps({'seq': self.connections[connection],
                                        'data': data}), connection)

    def receive(self):
        """Receive data with sequence number

        Verification of sequence message.
        If this is the first time we manage this connection, we add his sequence number
        as 0xffffffff for the connection phase (out of band messages).
        :return:
        """
        try:
            data, address = self.channel.recvfrom(BUFFER_SIZE)
            json_data = json.loads(data)
            seq_number, payload = json_data['seq'], json_data['data']

            if self.connections.get(address) is None:
                self.connections[address] = SEQ_OUTBAND

            if ((seq_number == SEQ_OUTBAND) or
                    (self.connections[address] < seq_number) or
                    (seq_number < self.connections[address] and (self.connections[address] - seq_number) > (1 << 31))):
                return payload, address
        except socket.error:
            # print "socket.error"
            pass

        return None, None
