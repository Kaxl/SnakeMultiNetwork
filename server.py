#!/usr/bin/python2.7
# -*- coding: utf-8 -*-



import socket               # Import socket module
import select
import random
import signal

from snake_channel import SnakeChannel

MAX_CLIENT = 10
UDP_IP = "127.0.0.1"
UDP_PORT = 5005
BUF_SIZE = 4096

class Server:
    def __init__(self, ip=UDP_IP, port=UDP_PORT):
        self.clients = {}
        self.outputs = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.ip = ip
        self.port = port
        self.server.bind((ip, port))
        # self.server.listen(10)
        print 'Listening to port', port, '...'

        # Trap keyboard interrupts
        #signal.signal(signal.SIGINT, self.sighandler)

    def waitConnections(self):
        # Num seq = 0xFFFFFFFF
        # 1. Wait for <<GetToken A Snake>>
        # 2. Send <<Token B A ProtocoleNumber>>
        # 3. Wait for <<Connect /nom_cle/val_cle/.../...>>
        # 4. Send <<Connected B>>
        while True:

            try:
                print "Wait for user"
                # 1. Wait for <<GetToken A Snake>>
                data_token, addr = self.server.recvfrom(BUF_SIZE)
                print "IN   - ", data_token

                token = data_token.split()
                A = token[1]
                # TODO Check if A already used
                B = random.randint(0, (1 << 32) - 1)
                # 2. Send <<Token B A ProtocoleNumber>>
                print "addr : ", addr
                self.server.sendto("Token " + str(B) + " " + str(A) + " " + str(SnakeChannel.protocol), addr)
                print "OUT   - Token ", B, " ", A, " ", SnakeChannel.protocol

                # 3. Wait for <<Connect /nom_cle/val_cle/.../...>>
                data_connect, addr = self.server.recvfrom(4096)
                print "IN   - ", data_connect

                token = data_connect.split()
                param = token[1].split('/')

                # Check the B value
                if len(param) < 3 or B != param[2]:
                    print "next"
                    continue

                # 4. Send <<Connected B>>
                self.server.sendto("Connected " + str(B),  (addr, self.port))
                print "OUT   - Connected ", B
            except socket.timeout:
                print 'Error timeout'

            inputready, outputready, exceptready = select.select(input, [], [])

            for s in inputready:
                if s == self.server:
                    conn, address = self.server.accept()
                    print 'got connection %d from %s' % (conn.fileno(), address)

                    try:
                        # 1. Wait for <<GetToken A Snake>>
                        data_token = self.server.recv(4096)
                        print "IN   - ", data_token

                        token = data_token.split()
                        A = token[1]
                        # TODO Check if A already used
                        B = random.randint(0, (1 << 32) - 1)
                        # 2. Send <<Token B A ProtocoleNumber>>
                        self.server.send("Token " + str(B) + " " + str(A) + " " + SnakeChannel.protocol)
                        print "OUT   - Token ", B, " ", A, " ", SnakeChannel.protocol

                        # 3. Wait for <<Connect /nom_cle/val_cle/.../...>>
                        data_connect = self.server.recv(4096)
                        print "IN   - ", data_connect

                        token = data_connect.split()
                        param = token[1].split('/')

                        # Check the B value
                        if B != param[2]:
                            continue

                        # 4. Send <<Connected B>>
                        self.server.send("Connected " + str(B))
                        print "OUT   - Connected ", B

                    except socket.timeout:
                        print 'Error timeout'

if __name__ == "__main__":
    s = Server()
    s.waitConnections()


# TODO
#class Server:
#
#    def accept_connextion(self):
#        return








