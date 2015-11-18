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
        self.listen()

if __name__ == "__main__":
    s = Server()
