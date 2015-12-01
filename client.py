#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket  # Import socket module
import time

from snake_post import *
from constants import *


class Client(SnakePost):
    """Class Client

    Inherits from SnakeChannel for its send and receive method.
    The client handle the connection and then waits for snakes update.
    """
    def __init__(self, ip='127.0.0.1', port=5006):
        """Initialization of Client class

        :param ip: IP of client
        :param port: Port of client
        :return:
        """
        super(Client, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
        self.ip = ip                    # IP of client
        self.port = int(port)           # Port of client
        self.channel.settimeout(2)      # Timeout
        self.connect()

    def hello_world_message(self):
        """Test function
        :return:
        """
        for i in range(1, 100):
            self.send_channel(str(self.connections[(IP_SERVER, PORT_SERVER)]) + " Test - Hello World", (IP_SERVER, PORT_SERVER))

if __name__ == "__main__":
    c = Client(port=5006)
    while True:
        # Send position to the server
        c.send_channel("Position")
        # Receive data from server
        c.receive_channel()
        c.receive_post()
        time.sleep(2)

