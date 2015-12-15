#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket  # Import socket module
import time
import pygame

from snake_post import *
from constants import *


class Client(SnakePost):
    """Class Client

    Inherits from SnakeChannel for its send and receive method.
    The client handle the connection and then waits for snakes update.
    """
    def __init__(self, ip, port):
        """Initialization of Client class

        :param ip: IP of client
        :param port: Port of client
        :return:
        """
        super(Client, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), ip, port)
        self.ip = ip                    # IP of client
        self.port = int(port)           # Port of client
        pygame.init()
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.connect()
        print "Connected"
        self.send_timer = Timer(SEND_INTERVAL, 0, True)

    def run(self):
        i = 0
        while True:

            #self.current_time += self.clock.tick(FPS)
            ## Send position to the server
            #if self.send_timer.expired(self.current_time):
            #    s = "Position" + str(i)
            #    i += 1
            #    self.send(s, secure=True)

            # self.send("")

            pos = "{'body_p':[ [0,0]"

            for x in range(0, 80, 1):
                for y in range(0, 25, 1):
                    pos += ",[" + str(x) + "," + str(y) + "]"

            pos += "] }"
            self.send(pos, secure=True)

            data = self.receive()
            if data is not None:
                print "[Client] Rcv : ", data

            self.process_buffer()

if __name__ == "__main__":
    c = Client(ip='129.194.186.177', port=8080)
    c.run()
