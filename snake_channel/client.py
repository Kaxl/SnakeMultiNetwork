#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket  # Import socket module
import random
from constants import *
from snake_channel import SnakeChannel


class Client(SnakeChannel):
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
        while state < 5:
            try:
                if state == 0:
                    # 1. Send <<GetToken A Snake>>
                    self.send("GetToken " + str(a) + " Snake", (IP_SERVER, PORT_SERVER), SEQ_OUTBAND)
                    print "OUT   - GetToken ", a, " Snake"
                    state += 1
                elif state == 1:
                    # 2. Wait for <<Token B A ProtocolNumber>>
                    ack_token, conn = self.receive()
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
                        self.send("Connect /challenge/" + str(b) + "/protocol/" + str(proto_number),
                                  (IP_SERVER, PORT_SERVER), SEQ_OUTBAND)
                        print "OUT  - Connect /challenge/", b, "/protocol/", proto_number
                        state += 1

                elif state == 3:
                    # 4. Wait for <<Connected B>>
                    ack_connect, conn = self.receive()
                    print "IN   - ", ack_connect
                    if ack_connect is None:
                        state = 2
                    else:
                        token = ack_connect.split()
                        b = token[1] # TODO : Store b value ?
                        state += 1
                elif state == 4:
                    # Client is connected
                    self.hello_world_message()
                    state += 1

                else:
                    print "Error during connection of client."
            except socket.timeout:
                # If timeout, return to state 0
                state = 0
        return

    def hello_world_message(self):
        """Test function
        :return:
        """
        for i in range(1, 100):
            self.send(str(self.connections[(IP_SERVER, PORT_SERVER)]) + " Test - Hello World", (IP_SERVER, PORT_SERVER))

if __name__ == "__main__":
    c = Client(port=5006)
