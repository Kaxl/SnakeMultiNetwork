#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

from snake_post import *
from constants import *


class Client(SnakeChannel):
    """Class Client

    Inherits from SnakeChannel for its send and receive method.
    The client handle the connection and then waits for snakes update.
    """
    def __init__(self, ip, port, color, nickname):
        """Initialization of Client class

        :param ip: IP of client
        :param port: Port of client
        :return:
        """
        super(Client, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), ip, port, color, nickname)
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

            self.current_time += self.clock.tick(FPS)
            # Send position to the server
            if self.send_timer.expired(self.current_time):
                #s = "{'body_p':[ [20,10],[20,11],[20,12],[20,13] ] }"
                s = "Hello from client : " + str(i)
                i += 1
                self.send_channel(s, (self.ip, self.port))

            data, conn = self.receive_channel()
            if data is not None:
                print "[Client] Rcv : ", data


if __name__ == "__main__":
    c = Client(ip=IP_SERVER, port=PORT_SERVER, color="yellow", nickname="pasquier")
    c.run()
