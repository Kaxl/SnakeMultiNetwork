#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import socket  # Import socket module
import random

from snake_channel import SnakeChannel

s = socket.socket()  # Create a socket object
host = socket.gethostname()  # Get local machine name
port = 12346  # Reserve a port for your service.

s.connect((host, port))
print(s.recv(1024))
s.close  # Close the socket when done


class Client:

    def __init__(self, host='127.0.0.1', port=1234):
        self.host = host
        self.port = int(port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.sock.setblocking(False)    # Non-blocking
        self.sock.settimeout(1)         # Timeout
        self.connect()

    def connect(self):
        # Num seq = 0xFFFFFFFF
        # 1. Send <<GetToken A Snake>>
        # 2. Wait for <<Token B A ProtocoleNumber>>
        # 3. Send <<Connect /nom_cle/val_cle/.../...>>
        # 4. Wait for <<Connected B>>
        state = 0
        A = random.randint(0, (1 << 32) - 1)
        while state < 4:
            #
            if state == 0:
                self.sock.connect((host, self.port))
                print 'Connect'
                # 1. Send <<GetToken A Snake>>
                self.sock.send("GetToken " + str(A) + " Snake")
                print "OUT   - GetToken ", A, " Snake"
                state += 1
            elif state == 1:
                # 2. Wait for <<Token B A ProtocoleNumber>>
                ack_token = self.sock.recv(4096)
                print "IN   - ", ack_token
                if ack_token is None:
                    state = 0
                else:
                    state += 1
            elif state == 2:
                token = ack_token.split()
                # Check if A value is correct
                if token[2] != A:
                    state = 0
                else:
                    B, proto_number = token[1], token[3]
                    self.sock.send("Connect /challenge/" + str(B) + "/protocol/" + str(proto_number))
                    print "OUT   - Connect /challenge/", B, "/protocol/", proto_number
                    state += 1
            elif state == 3:
                ack_connect = self.sock.recv(4096)
                print "IN   - ", ack_connect
                if ack_connect is None:
                    state = 2
                else:
                    token = ack_connect.split()
                    B = token[1]
                    state += 1
            else:
                print "Error during connection of client."

        return

    def close(self):
        return

# class SnakeChannel

# class Token:
#    """Structure de base d'un token (num_seq, data, ...)"""
#
#    num_seq = 1



"""
TODO
Faire une horloge globale.

A chaque iteration, verifier s'il faut renvoyer le message (si le temps requis
est depasse, on renvoie)


IP UDP(HEADER) SNAKECHAN PAYLOAD


"""
