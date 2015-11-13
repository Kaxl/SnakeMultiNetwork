#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
import random
from snake_channel import SnakeChannel

from constants import *


class Server(SnakeChannel):
    """Class Server

    Inherits from SnakeChannel for its send and receive method.
    The server waits for messages.
    If the state is in the connection phase, we handle de connection of the client.
    If the state is already established for the client, we handle the game positions.
    """
    def __init__(self, ip=IP_SERVER, port=PORT_SERVER):
        """Initialization of Server class

        :param ip: IP of server
        :param port: Port of server
        :return:
        """
        super(Server, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        self.ip = ip                        # IP of server
        self.port = port                    # Port of server
        self.channel.setblocking(False)     # Non-blocking
        self.channel.bind((self.ip, self.port))
        print 'Listening to port', self.port, '...'

    def message_management(self):
        """Management of messages

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

        while True:
            try:
                # 1. Wait for <<GetToken A Snake>>
                data, conn = self.receive()

                if data is None:
                    continue

                # Parse data to get the State
                state = data.split()[0]

                if state == STATE_1_S:
                    self.connections[conn] = 0
                    print "IN   - ", data

                    token = data.split()
                    A = token[1]
                    # TODO Check if A already used

                    # Generate random B
                    B = random.randint(0, (1 << 32) - 1)
                    # 2. Send <<Token B A ProtocolNumber>>
                    self.send("Token " + str(B) + " " + str(A) + " " + str(PROTOCOL_NUMBER), conn, SEQ_OUTBAND)
                    print "OUT  - Token ", B, " ", A, " ", PROTOCOL_NUMBER

                elif state == STATE_2_S:
                    # 3. Wait for <<Connect /challenge/B/protocol/...>>
                    if data is None:
                        continue

                    print "IN   - ", data
                    # Split data and get the parameters
                    token = data.split()
                    param = token[1].split('/')

                    # Check the B value
                    if len(param) < 3 or int(B) != int(param[2]):
                        continue

                    # 4. Send <<Connected B>>
                    self.send("Connected " + str(B), conn, SEQ_OUTBAND)
                    print "OUT  - Connected ", B
                    self.connections[conn] = 0

                elif state == STATE_3_S:
                    # Client is connected
                    pass
                else:
                    print data

            except socket.timeout:
                print 'Error timeout'

if __name__ == "__main__":
    s = Server()
    s.message_management()
