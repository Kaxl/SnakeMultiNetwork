#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys

sys.path.append('..')

from snake_post import *
from constants import *
import json
from player import *


class SnakeServer(SnakePost):
    def __init__(self):
        super(SnakeServer, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), Constants.IP_SERVER,
                                          Constants.PORT_SERVER)
        pygame.init()
        self.clock = pygame.time.Clock()

        self.ip = Constants.IP_SERVER
        self.port = Constants.PORT_SERVER
        self.channel.setblocking(False)  # Non-blocking
        self.channel.bind((self.ip, self.port))

        # Dict of Player object
        # Key is the connection, value if a player object
        self.players = {}

        # List of foods
        self.foods = []

        #self.current_time = 0

        self.new_apple_timer = Timer(Constants.NEW_APPLE_PERIOD * 1000, self.current_time, periodic=True)
        self.send_snakes_timer = Timer(Constants.SNAKES_PERIOD * 1000, self.current_time, periodic=True)
        self.check_activity_timer = Timer(Constants.ACTIVITY_PERIOD * 1000, self.current_time, periodic=True)
        print "Server initialized"

    def run(self):
        while True:
            #self.current_time += self.clock.tick(FPS)
            # Process message to send
            self.process_buffer()

            # Receive data
            data, conn = self.listen()

            # Check if new connection
            if data is not None and not self.players.get(conn):
                self.players[conn] = Player(self.connections[conn][D_NICKNAME], self.connections[conn][D_COLOR], 0,
                                            False, [])
                # Send "players_info" to players
                self.broadcast(self.create_msg("players_info"), True)

                # Send foods positions (only to the new player)
                self.send(self.create_msg("foods"), conn, True)

            if data is not None:
                try:
                    data_json = json.loads(data)
                    for key in data_json:
                        if key == 'body_p':
                            # Update the position of the snake
                            if self.players.get(conn):
                                self.players[conn].positions = data_json[key]

                            # If player is not ready, pass
                            if not self.players[conn].ready:
                                continue

                            # If head is on an apple
                            for pos in self.foods:
                                if self.players[conn].positions[0] == pos:
                                    # Remove apple from the list
                                    self.foods.remove(pos)
                                    self.broadcast(self.create_msg("grow", self.players[conn].name), True)
                                    # Send list of foods
                                    self.broadcast(self.create_msg("foods"), True)
                                    break

                            # Check for collisions
                            # Loop over each players
                            for p in self.players:
                                if not self.players[p].ready:
                                    continue
                                # Loop over each position of player
                                for pos in self.players[p].positions:
                                    # If we check the current player, check if a position if present two times
                                    if p == conn:
                                        if self.players[conn].positions.count(self.players[conn].positions[0]) > 1:
                                            # Send "game over"
                                            self.broadcast(self.create_msg("game_over", self.players[conn].name))
                                            # Decrement score of player
                                            self.players[conn].score -= 1

                                            # Change state of player to not ready
                                            self.players[conn].ready = False

                                            # Resend a players_info to change the score
                                            self.broadcast(self.create_msg("players_info"))
                                            break
                                    else:
                                        # If a position of player is the same as the new head
                                        if self.players[conn].positions[0] == pos:
                                            # Send "game over"
                                            self.broadcast(self.create_msg("game_over", self.players[conn].name))

                                            # If the player was "hit" by another player he wins 1 point
                                            if p != conn:
                                                self.players[p].score += 1
                                            else:
                                                # Decrement score of player
                                                self.players[conn].score -= 1

                                            # Change state of player to not ready
                                            self.players[conn].ready = False

                                            # Resend a players_info to change the score
                                            self.broadcast(self.create_msg("players_info"))
                                            break

                        elif key == 'ready':
                            # set the state of the snake as ready
                            if self.players.get(conn):
                                self.players[conn].ready = data_json[key]

                            # Send "players_info" message
                            self.broadcast(self.create_msg("players_info"), True)
                        break
                    if self.players.get(conn):
                        self.players[conn].last_update = self.current_time
                except:
                    #print "Exception server"
                    pass

            # Check if game need more food
            if self.new_apple_timer.expired(self.current_time) and len(self.foods) < Constants.MAX_APPLE_SAME_TIME:
                self.foods.append([random.randint(0, Constants.UNITS - 1), random.randint(0, Constants.UNITS - 1)])
                self.broadcast(self.create_msg("foods"), True)

            # Check for clients timeout
            # If timeout, removed from the dictionary
            players_to_remove = [key for key in self.players
                                 if self.players[key].timeout(self.current_time)]

            for key in players_to_remove:
                del self.players[key]
                del self.connections[key]

            # Check if we need to send snakes positions
            if self.send_snakes_timer.expired(self.current_time):
                self.broadcast(self.create_msg("snakes"), False)

    def create_msg(self, type, player=None):
        """
        Creation of message depending of the type

        :param type: Type of message
        :param player: player depending on message
        :return:
        """
        if type == "foods":
            msg = "{\"foods\": " + str(self.foods) + "}"
        elif type == "players_info":
            msg = "{\"players_info\": ["
            for key in self.players:
                msg += "[\"" + str(self.players[key].name) + "\",\"" + str(self.players[key].color) + \
                       "\"," + str(self.players[key].score) + "," + str(self.players[key].ready).lower() + "],"
            msg = msg[:-1]
            msg += "]}"
        elif type == "snakes":
            msg = "{\"snakes\": ["
            for key in self.players:
                msg += "[\"" + str(self.players[key].name) + "\"," + str(self.players[key].positions) + "],"
            msg = msg[:-1]
            msg += "]}"
        elif type == "grow":
            msg = "{\"grow\": \"" + str(player) + "\"}"
        elif type == "game_over":
            msg = "{\"game_over\": \"" + str(player) + "\"}"
        else:
            return None
        return msg

    def broadcast(self, msg, secure=False):
        """
        Broadcast data to every client

        :param msg: Message to send
        :param secure: If secure or not
        :return:
        """
        for conn in self.players:
            self.send(msg, conn, secure)


if __name__ == "__main__":
    SnakeServer().run()
