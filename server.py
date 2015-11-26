#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket
from snake_post.snake_post import SnakePost

from constants import *


class Server(SnakePost):
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

        while True:
            data = self.listen()
            if data is not None:
                print "Data : ", data

            data_secure = self.listen_secure()
            if data_secure is not None:
                pass
                #if data = position
                #    broadcast position
                #else if data = mange pomme
                #    broacast info

                #if new apple:
                #    self.send_post()


if __name__ == "__main__":
    s = Server()
