#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from snake_post import *
from constants import *


class ClientUDP(SnakePost):
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
        super(ClientUDP, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), True)
        self.ip = ip                    # IP of client
        self.port = int(port)           # Port of client
        pygame.init()
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.channel.bind((self.ip, self.port))
        self.channel.setblocking(False)
        self.send_timer = Timer(SEND_INTERVAL, 0, True)

    def run(self):
        i = 0
        server = ('127.0.0.1', 5005)
        self.connections[server] = []
        while True:
            self.current_time += self.clock.tick(FPS)
            # Send position to the server
            if self.send_timer.expired(self.current_time):
                s = "Position" + str(i)
                i += 1
                self.send(s, server, True)

            data = self.receive()
            if data is not None:
                print "[Client] Rcv : ", data

            self.process_buffer()

if __name__ == "__main__":
    c = ClientUDP(port=5006)
    c.run()

