#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import sys

sys.path.append('..')

from object_snake import *
from object_foods import *
from scores import *
from preferences import Preferences
from banner import *
from snake_post import *
from constants import *
import json


class SnakeClient(SnakePost):
    def __init__(self, ip, port, color, nickname):
        super(SnakeClient, self).__init__(socket.socket(socket.AF_INET, socket.SOCK_DGRAM), ip, port, color, nickname)
        self.ip = ip  # IP of client
        self.port = int(port)  # Port of client

        pygame.init()
        self.clock = pygame.time.Clock()
        self.current_time = 0
        self.connect()
        print "Connected"
        self.send_timer = Timer(SEND_INTERVAL, 0, True)

        # get preferences
        self.preferences = Preferences()

        # resolution, flags, depth, display
        self.unit = Constants.RESOLUTION[0] / Constants.UNITS
        self.banner = Banner()
        self.score_width = self.unit * 15

        if self.preferences.fullscreen:
            self.screen = pygame.display.set_mode((Constants.RESOLUTION[0] + self.score_width, \
                                                   Constants.RESOLUTION[1]), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((Constants.RESOLUTION[0] + self.score_width, \
                                                   Constants.RESOLUTION[1]), 0, 32)

        pygame.display.set_caption(Constants.CAPTION)

        # game area surface
        self.gamescreen = pygame.Surface(Constants.RESOLUTION)
        # score area rectangle surface
        self.scorescreen = pygame.Surface((self.score_width, Constants.RESOLUTION[1]))

        # Snake and foods manager
        # self.me = Snake(color=pygame.color.THECOLORS[self.preferences.get("color")], \
        #                nickname=self.preferences.get("nickname"))

        self.me = Snake(color=pygame.color.THECOLORS[color],
                        nickname=nickname)

        # self.nickname = self.preferences.get("nickname")
        self.f = Foods()

        # Dict of Snake object
        self.snakes = {}

        # Score manager
        self.scores = Scores((self.score_width, Constants.RESOLUTION[1]))

        # add our own score, the server will send us the remaining one at connection
        # self.scores.new_score(self.preferences.get("nickname"), \
        #                      pygame.color.THECOLORS[self.preferences.get("color")])

        # game area background color
        self.gamescreen.fill(Constants.COLOR_BG)
        self.scorescreen.fill((100, 100, 100))

        # timers
        self.clock = pygame.time.Clock()
        self.current_time = 0

        self.move_snake_timer = Timer(1.0 / Constants.SNAKE_SPEED * 1000, self.current_time, periodic=True)
        self.blink_snake_timer = Timer(1.0 / Constants.SNAKE_BLINKING_SPEED * 1000, self.current_time, periodic=True)
        self.blink_banner_timer = Timer(500, self.current_time, periodic=True)
        self.new_apple_timer = Timer(Constants.NEW_APPLE_PERIOD * 1000, self.current_time, periodic=True)

    def process_events(self):
        # key handling
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_UP:
                    self.me.action(1)
                if event.key == pygame.K_DOWN:
                    self.me.action(2)
                if event.key == pygame.K_LEFT:
                    self.me.action(3)
                if event.key == pygame.K_RIGHT:
                    self.me.action(4)
                if event.key == pygame.K_SPACE:
                    self.send("{\"ready\": true }", (self.ip, self.port), True)
                    self.me.set_ready()

    def run(self):
        whole_second = 0
        self.running = True
        while self.running:

            # Process message to send
            self.process_buffer()

            # Receive data
            try:
                data, conn = self.receive()
                if data is not None:
                    # print "[Client] Rcv : ", data
                    data_json = json.loads(data)
                    # print data_json
                    for key in data_json:
                        if key == 'foods':
                            # Update the list of apples
                            self.f.set_positions(data_json[key])
                        elif key == 'snakes':
                            # Find players that no longer exists
                            # and remove them from the list
                            for name in self.snakes.keys():
                                found = False
                                for data in data_json[key]:
                                    if data[0] == name:
                                        found = True

                            for value in data_json[key]:
                                if self.snakes.get(value[0]):
                                    self.snakes[value[0]].setBody(value[1])
                                    # print "snakes"
                        elif key == 'players_info':
                            # Parse the players_info
                            for player_info in data_json[key]:

                                # First time connection of a player
                                if not self.snakes.get(player_info[0]):
                                    self.snakes[player_info[0]] = Snake(color=pygame.color.THECOLORS[player_info[1]],
                                                                        nickname=player_info[0])
                                    self.scores.new_score(player_info[0], self.snakes[player_info[0]].color)

                                # Player is already connected, updating his scores
                                else:
                                    # Set ready
                                    if player_info[3]:
                                        self.snakes[player_info[0]].set_ready()
                                    # Set the scores
                                    self.scores.set_score(player_info[0], player_info[2])

                        elif key == 'game_over':
                            # Start the game at the start
                            if data_json[key] == self.nickname:
                                self.snakes[data_json[key]].restart()
                                self.me.restart()
                                self.snakes[data_json[key]].ready = False
                                self.me.ready()

                            # Set the player who had game over at not ready
                            self.snakes[data_json[key]].ready = False

                        elif key == 'grow':
                            # If client is concerned, increment its size
                            if data_json[key] == self.nickname:
                                self.me.grow(Constants.GROW)
                                # self.snakes[data_json[key]].grow(Constants.GROW)
                        break
            except:
                print "Exception client"
                pass

            # time tracking
            self.current_time += self.clock.tick(Constants.FPS)

            # check if the snake is still alive
            # if not self.me.alive:
            #    self.me.alive = True
            #    self.me.restart()

            # check if game need more food
            # if self.new_apple_timer.expired(self.current_time):
            #    self.f.make()

            # check if we need to move our own snake's state
            # if we do, send an update of our position to
            # the server
            if self.move_snake_timer.expired(self.current_time):
                self.me.move()
                s = "{\"body_p\":" + str(self.me.body) + " }"
                s = self.me.netinfo()
                # print s
                self.send(s, (self.ip, self.port), secure=False)

            # check if we need to blink the unready snakes (unready state)
            if self.blink_snake_timer.expired(self.current_time):
                for snake in self.snakes:
                    self.snakes[snake].blink()

                    # check if snake has eaten
                    #if self.me.ready:
                    #    if self.f.check(self.me.head):
                    #        self.me.grow(Constants.GROW)
                    #        self.scores.inc_score(self.nickname, 1)

            # cleanup background
            self.gamescreen.fill(Constants.COLOR_BG)

            # draw scores
            self.scores.draw(self.screen)

            # draw all snakes positions as last seen by the server
            # we do not compute their positions ourselves!
            for snake in self.snakes:
                self.snakes[snake].draw(self.gamescreen)

            # draw food
            self.f.draw(self.gamescreen)

            # process external events (keyboard,...)
            self.process_events()

            # then update display
            # update game area on screen container
            self.screen.blit(self.gamescreen, (self.score_width, 0))

            pygame.display.update()


if __name__ == "__main__":
    SnakeClient(Constants.IP_SERVER, Constants.PORT_SERVER, "pink", "gerome").run()
    #SnakeClient(Constants.IP_SERVER, 7777, "green", "pasquier").run()
    # SnakeClient("127.0.0.1", Constants.PORT_SERVER, "green", "tinder_guy").run()
    # SnakeClient("192.168.1.42", 21025, "red", "pasqueir").run()
    #SnakeClient("192.168.1.42", 21025, "yellow", "nyancat").run()
