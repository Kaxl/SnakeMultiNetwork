#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

IP_SERVER = "127.0.0.1"
PORT_SERVER = 5005
BUFFER_SIZE = 4096
PROTOCOL_NUMBER = 19
SEQ_OUTBAND = 0xffffffff    # Message for the connection

# State for the server
STATE_1_S = "GetToken"
STATE_2_S = "Connect"
STATE_3_S = "Game"

# Index for dictionary of server
D_SEQNUM = 0    # Sequence number
D_STATUS = 1    # Status (connected / not connected)
D_LASTP = 2     # Last ping

