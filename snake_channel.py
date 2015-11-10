#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

class SnakeChannel:

    # List of sockets
    channel = []
    protocol = 19

    def __init__(self, channel):
        self.channel = channel

    def request(self):
        """Client part"""
        # Num seq = 0xFFFFFFFF
        # 1. Send <<GetToken A Snake>>
        # 2. Wait for <<Token B A ProtocolNumber>>
        # 3. Send <<Connect /nom_cle/val_cle/.../...>>
        # 4. Wait for <<Connected B>>
        pass

    def listen(self):
        """Server part"""
        # Num seq = 0xFFFFFFFF
        # 1. Wait for <<GetToken A Snake>>
        # 2. Send <<Token B A ProtocolNumber>>
        # 3. Wait for <<Connect /nom_cle/val_cle/.../...>>
        # 4. Send <<Connected B>>
        pass

    def send(self):
        """Send data with sequence number"""
        # Num seq++
        # Send (NumSeq, Data)


    def receive(self):
        """Receive data with sequence number"""
