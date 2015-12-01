# -*- coding: utf-8 -*-

import pygame
from constants import Constants
from object_snake import *
from object_foods import *
from scores import *
from preferences import Preferences
from banner import *
from timer import *

class Game:
    def __init__(self):
        pygame.init()
        
        #get preferences
        self.preferences = Preferences() 

        #resolution, flags, depth, display
        self.unit=Constants.RESOLUTION[0]/Constants.UNITS
        self.banner = Banner()
        self.score_width=self.unit*15

        if self.preferences.fullscreen:
            self.screen = pygame.display.set_mode((Constants.RESOLUTION[0]+self.score_width,\
                                               Constants.RESOLUTION[1]),pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((Constants.RESOLUTION[0]+self.score_width,\
                                               Constants.RESOLUTION[1]),0,32)
        
        pygame.display.set_caption(Constants.CAPTION)
        
        #game area surface
        self.gamescreen = pygame.Surface(Constants.RESOLUTION)
        #score area rectangle surface
        self.scorescreen = pygame.Surface((self.score_width,Constants.RESOLUTION[1]))

        #Snake and foods manager 
        self.me=Snake(color=pygame.color.THECOLORS[self.preferences.get("color")],\
                     nickname=self.preferences.get("nickname"))
        
        self.nickname = self.preferences.get("nickname")
        self.f=Foods()

        #Score manager
        self.scores=Scores((self.score_width,Constants.RESOLUTION[1]))
        
        #add our own score, the server will send us the remaining one at connection
        self.scores.new_score(self.preferences.get("nickname"),\
                        pygame.color.THECOLORS[self.preferences.get("color")])

	#game area background color
        self.gamescreen.fill(Constants.COLOR_BG)
        self.scorescreen.fill((100,100,100))
        
        #timers
        self.clock=pygame.time.Clock();
        self.current_time=0
        
        self.move_snake_timer=Timer(1.0/Constants.SNAKE_SPEED*1000,self.current_time,periodic=True)
        self.blink_snake_timer=Timer(1.0/Constants.SNAKE_BLINKING_SPEED*1000,self.current_time,periodic=True)
        self.blink_banner_timer=Timer(500,self.current_time,periodic=True)
        self.new_apple_timer=Timer(Constants.NEW_APPLE_PERIOD*1000,self.current_time,periodic=True)

    def process_events(self):
        #key handling
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                   self.running=False 
                if event.key == pygame.K_UP:
                   self.me.action(1)
                if event.key == pygame.K_DOWN:
                   self.me.action(2)
                if event.key == pygame.K_LEFT:
                   self.me.action(3)
                if event.key == pygame.K_RIGHT:
                   self.me.action(4)
                if event.key == pygame.K_SPACE:
                   self.me.set_ready()

    def run(self):
        whole_second=0
        self.running=True
        while self.running:
            #time tracking
            self.current_time+=self.clock.tick(Constants.FPS) 
          
            #check if the snake is still alive
            if not self.me.alive:
                self.me.alive=True
                self.me.restart()

            #check if game need more food
            if self.new_apple_timer.expired(self.current_time):
                self.f.make()

            #check if we need to move our own snake's state
            #if we do, send an update of our position to 
            #the server
            if self.move_snake_timer.expired(self.current_time):
                self.me.move()

            #check if we need to blink the unready snakes (unready state)
            if self.blink_snake_timer.expired(self.current_time):
                self.me.blink()

            #check if snake has eaten
            if self.me.ready:
                if self.f.check(self.me.head):
                    self.me.grow(Constants.GROW)
                    self.scores.inc_score(self.nickname,1)

            #cleanup background
            self.gamescreen.fill(Constants.COLOR_BG)
            
            #draw scores
            self.scores.draw(self.screen)
            
            #draw all snakes positions as last seen by the server
            #we do not compute their positions ourselves!
            self.me.draw(self.gamescreen) 
                
            #draw food
            self.f.draw(self.gamescreen)
            
            #process external events (keyboard,...)
            self.process_events()

            #then update display
            #update game area on screen container
            self.screen.blit(self.gamescreen,(self.score_width,0)) 
	    
            pygame.display.update()
            
Game().run()
