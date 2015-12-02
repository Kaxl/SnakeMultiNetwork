#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from snake_post import *
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
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.send_timer = Timer(SEND_INTERVAL, 0, True)
        print 'Listening to port', self.port, '...'

    def run(self):
        while True:
            self.current_time += self.clock.tick(60)
            data = self.listen()
            if data is not None:
                print "[Server] Rcv : ", data
                # Process game

            # Broadcast data
            # Broadcast new apple secure
            if self.send_timer.expired(self.current_time):
                for c in self.connections:
                    self.send("kikoo", c)

            self.process_buffer()

if __name__ == "__main__":
    s = Server()
    s.run()
