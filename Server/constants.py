#  YetAnotherPythonSnake 0.92
#  Author: Simone Cingano (simonecingano@gmail.com)
#  Web: http://simonecingano.it
#  Licence: MIT
#

import os

class Constants:
    """ All of the in-game constants are declared here."""

    # Constants for index of list
    D_COLOR = 0
    D_SCORE = 1
    D_READY = 2

    # Info server
    IP_SERVER = "127.0.0.1"
    PORT_SERVER = 8080

    # FPS
    FPS = 60
    UNITS = 40

    #In one apple every X seconds
    NEW_APPLE_PERIOD = 5
    SNAKES_PERIOD = 0.1
    ACTIVITY_PERIOD = 2

    TIMEOUT_PLAYER = 2

    #maximum number of apple at the same time on the board
    MAX_APPLE_SAME_TIME = 5

    START_LENGTH = 5

    #by how much the snake will grow for each apple
    GROW = 2

