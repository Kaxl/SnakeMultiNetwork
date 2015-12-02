#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import struct
import random
from constants import *


class SnakeChannel(object):
    """Class SnakeChannel

    Handle the send and receive of messages protocol.
    This class is inherited by Client and Server class to send and receive message.
    It contains a channel (socket) and a dictionary of connections :
    key : (ip, port)
    value : (sequence number, connected, last ping)

    sequence number : last sequence number of client
    connected : boolean value to know if client is connected
    last ping : last time the client contacted the server
                If this value reach the time out, the client is disconnected

    TODO : Do we need to have the B value for security issues ? (crypt / decrypt)
    """
    def __init__(self, channel):
        """Initialization of SnakeChannel

        :param channel: Socket for the connection
        :return:
        """
        self.channel = channel
        self.channel.setblocking(False)
        self.channel.settimeout(2)
        self.connections = {}
        self.local_seq_number = {}
        self.b = 0

    def listen_channel(self):
        """Listen to clients

        Handle the connection and the game

        States :
        Num seq = 0xFFFFFFFF
        1. Wait for <<GetToken A Snake>>
        2. Send <<Token B A ProtocoleNumber>>
        3. Wait for <<Connect /nom_cle/val_cle/.../...>>
        4. Send <<Connected B>>

        After the connection phase :
        The server sends game info to the clients
        :return:
        """
        try:
            # Receive data from client
            data, conn = self.receive_channel()

            if data is None:
                return None, None

            # Check if client is connected
            if not self.connections[conn][D_STATUS]:
                # Connection logic
                # Parse data to get the State
                state = data.split()[0]

                # 1. Wait for <<GetToken A Snake>>
                if state == STATE_1_S:
                    self.connections[conn][D_SEQNUM] = 0
                    print "IN   - ", data

                    token = data.split()
                    a = token[1]

                    # Generate random B
                    self.b = random.randint(0, (1 << 32) - 1)

                    # 2. Send <<Token B A ProtocolNumber>>
                    self.send_channel("Token " + str(self.b) + " " + str(a) + " " + str(PROTOCOL_NUMBER), conn, SEQ_OUTBAND)
                    print "OUT  - Token ", self.b, " ", a, " ", PROTOCOL_NUMBER

                elif state == STATE_2_S:
                    # 3. Wait for <<Connect /challenge/B/protocol/...>>
                    if data is None:
                        return None, None

                    print "IN   - ", data
                    # Split data and get the parameters
                    token = data.split()
                    param = token[1].split('/')

                    # Check the B value
                    if len(param) < 3 or int(self.b) != int(param[2]):
                        return None, None

                    # 4. Send <<Connected B>>
                    self.send_channel("Connected " + str(self.b), conn, SEQ_OUTBAND)
                    print "OUT  - Connected ", self.b
                    self.connections[conn][D_STATUS] = True
            else:
                # Client is connected, return the data
                return data, conn

        except socket.timeout:
            #print 'Error timeout'
            pass
        return None, None

    def connect(self):
        """Connection of clients

        States of connection :
        Num seq = 0xFFFFFFFF
        1. Send <<GetToken A Snake>>
        2. Wait for <<Token B A ProtocolNumber>>
        3. Send <<Connect /nom_cle/val_cle/.../...>>
        4. Wait for <<Connected B>>

        After the connection :
        Receive game info
        :return:
        """
        state = 0
        ack_token = ""
        a = random.randint(0, (1 << 32) - 1)
        while state < 4:
            try:
                if state == 0:
                    # 1. Send <<GetToken A Snake>>
                    self.send_channel("GetToken " + str(a) + " Snake", (IP_SERVER, PORT_SERVER), SEQ_OUTBAND)
                    print "OUT   - GetToken ", a, " Snake"
                    state += 1
                elif state == 1:
                    # 2. Wait for <<Token B A ProtocolNumber>>
                    ack_token, conn = self.receive_channel()
                    print "IN   - ", ack_token
                    if ack_token is None:
                        state = 0
                    else:
                        state += 1

                elif state == 2:
                    # 3. Send <<Connect /nom_cle/val_cle/.../...>>
                    token = ack_token.split()
                    # Check if A value is correct
                    if int(token[2]) != int(a):
                        state = 0
                    else:
                        b, proto_number = token[1], token[3]
                        self.send_channel("Connect /challenge/" + str(b) + "/protocol/" + str(proto_number),
                                          (IP_SERVER, PORT_SERVER), SEQ_OUTBAND)
                        print "OUT  - Connect /challenge/", b, "/protocol/", proto_number
                        state += 1

                elif state == 3:
                    # 4. Wait for <<Connected B>>
                    ack_connect, conn = self.receive_channel()
                    print "IN   - ", ack_connect
                    if ack_connect is None:
                        state = 2
                    else:
                        token = ack_connect.split()
                        self.b = token[1]
                        state += 1
                else:
                    print "Error during connection of client."
            except socket.timeout:
                # If timeout, return to state 0
                state = 0
        return

    def send_channel(self, data, connection=(IP_SERVER, PORT_SERVER), seq=None):
        """Send data with sequence number

        Connection as a default value (IP server and port server)

        If a sequence number is provided and is 0xffffffff, then this
        is an outbound message and we process it.
        Else, we increment the sequence number.

        :param data: data to send
        :param connection: connection (ip, port)
        :param seq: sequence number if provided
        """
        if self.local_seq_number.get(connection) is None:
            self.local_seq_number[connection] = SEQ_OUTBAND

        if seq is None:  # Incrementation of sequence number (modulo)
            self.local_seq_number[connection] = (self.local_seq_number[connection] + 1) % (0x1 << 32)
        else:  # Sequence number is 0xFFFFFFFF -> connection packet
            self.local_seq_number[connection] = seq

        # Pack the sequence number
        pack = struct.pack('>I', self.local_seq_number[connection])
        # Concatenation of data
        pack += data

        # Send the message
        self.channel.sendto(pack, connection)

    def receive_channel(self):
        """Receive data with sequence number

        Verification of sequence message.
        If this is the first time we manage this connection, we add his sequence number
        as 0xffffffff for the connection phase (out of band messages).
        :return:
        """
        try:
            data, address = self.channel.recvfrom(BUFFER_SIZE)
            seq_number = struct.unpack('>I', data[:4])[0]
            payload = data[4:]

            if self.connections.get(address) is None:
                self.connections[address] = [SEQ_OUTBAND, False, 0]

            if ((seq_number == SEQ_OUTBAND) or
                    (self.connections[address][D_SEQNUM] < seq_number) or
                    (seq_number < self.connections[address][D_SEQNUM] and (self.connections[address][D_SEQNUM] - seq_number) > (1 << 31))):
                self.connections[address][D_SEQNUM] = seq_number
                return payload, address
        except socket.error:
            #print "socket.error"
            pass

        return None, None
