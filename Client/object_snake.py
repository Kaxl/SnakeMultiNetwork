#
#  YetAnotherPythonSnake 0.92
#  Author: Simone Cingano (simonecingano@gmail.com)
#  Web: http://simonecingano.it
#  Licence: MIT
#

import pygame
import random
import json
from constants import Constants

class SnakeBlockKind:
    HEAD = 0
    BODY = 1
    NOTHING = 2

class Snake(object):

    #self.unit is the size of a square that composes the snake
    def __init__(self, unit=Constants.RESOLUTION[0]/Constants.UNITS, color=((255,0,0)), nickname="chicken"):
        self.ready=False
        self.unit = unit
        self.alive = True
        self.current_color = color
        self.color = color
        self.nickname = nickname
        
        # Initial orientation
        # and its meaning on the x,y directions.
        self.vx = 0
        self.vy = -1

        self.movelock = False #prevent double move between clock

        self.head = None #head block position
        self.tail = None #removed block position

        self.body = []          # sprites relative coordinates
        self.body_sprites = []  # sprites pixels content and absolute coordinates
        self.after_the_tail_sprite = None
        self.length = 0

        #put first body block right  in the middle of the grid (0,0 is the upper left pixel)
        self.addBody((int(0.5*Constants.UNITS),int(0.5*Constants.UNITS)))
        
        #the snake will start growing up to this value
        #we remove one as one body has been added in the constructor
        self.growmore = Constants.START_LENGTH-1

    def restart(self):
        self.vx = 0
        self.vy = -1
        
        self.head = None #head block position
        self.tail = None #removed block position

        self.body = []          # sprites relative coordinates
        self.body_sprites = []  # sprites pixels content and absolute coordinates
        self.after_the_tail_sprite = None
        self.length = 0

        #put first body block right  in the middle of the grid (0,0 is the upper left pixel)
        self.addBody((int(0.5*Constants.UNITS),int(0.5*Constants.UNITS)))
        
        #the snake will start growing up to this value
        #we remove one as one body has been added in the constructor
        self.growmore = Constants.START_LENGTH-1
        self.ready=False


    def get_forbidden(self):
        coords = []
        for el in self.body_sprites:
            coords.append([int(el.rect.x/self.unit),int(el.rect.y/self.unit)])
        return coords

    def setBody(self,positions):
        self.body = positions
        self.length = len(positions)
        self.body_sprites = []
        
        b=SnakeBlock(self.unit,positions[0],SnakeBlockKind.HEAD)
        self.body_sprites.append(b)

        for p in positions[1:]:
            b=SnakeBlock(self.unit,p,SnakeBlockKind.BODY,self.current_color)
            self.body_sprites.append(b)
        
        self.head = positions[0]
        self.tail = positions[-1]

    def setBodyColor(self,color):
        self.current_color=color
        for el in self.body_sprites[1:]:
                el.update_color(self.current_color)

    def addBody(self,position):
        #1. sprites[0] is the head : head becomes body.
        if self.length > 0:
            self.body_sprites[0].update_kind(SnakeBlockKind.BODY,self.current_color)
        #add new head at position 
        b = SnakeBlock(self.unit,position,SnakeBlockKind.HEAD)
        self.body.insert(0,position)
        self.body_sprites.insert(0,b)
        self.head = position
        self.length+=1

    def removeBody(self):
        self.after_the_tail_sprite=x= self.body_sprites.pop()
        self.after_the_tail_sprite.update_kind(SnakeBlockKind.NOTHING,Constants.COLOR_BG)
        self.tail = self.body.pop()
        self.length-=1
        del x

    def set_dirty(self,dirty):
        for el in self.body_sprites:
            el.dirty = dirty

    def set_unready(self):
        self.ready=False

    def set_ready(self):
        self.setBodyColor(self.color)
        self.ready=True

    def blink(self):
        if not self.ready:
            if self.current_color == self.color:
                self.setBodyColor((0,0,0))
            elif self.current_color == (0,0,0):
                self.setBodyColor(self.color)

    def draw(self,surface):
        for el in self.body_sprites:
            surface.blit(el.image,el.rect)
        if self.after_the_tail_sprite:
            surface.blit(self.after_the_tail_sprite.image, self.after_the_tail_sprite.rect)

    def action(self, movement):
        if self.movelock: return
        """ Handle keyboard events. """
        if movement==1:
            if self.vy == 1: return
            self.vx = 0
            self.vy = -1
        elif movement==2:
            if self.vy == -1: return
            self.vx = 0
            self.vy = 1
        elif movement==3:
            if self.vx == 1: return
            self.vx = -1
            self.vy = 0
        elif movement==4:
            if self.vx == -1: return
            self.vx = 1
            self.vy = 0
        self.movelock = True

    def get_x(self,index=0):
        return self.body[index][0]

    def get_y(self,index=0):
        return self.body[index][1]

    def grow(self,size=1):
        self.growmore+=size

    def move(self):
        next = [self.get_x()+self.vx,self.get_y()+self.vy]

        #this is where we check if the snake eats itself
        if self.ready:
            if next in self.body:
                self.alive = False

        # exit left, appear right and so on
        if next[0] < 0: next[0] = Constants.UNITS-1
        if next[0] > Constants.UNITS-1: next[0] = 0
        if next[1] < 0: next[1] = Constants.UNITS-1
        if next[1] > Constants.UNITS-1: next[1] = 0

        self.addBody(next)

        if self.growmore:
            self.growmore-=1
            #self.length+=1
        else:
            self.removeBody()

        self.movelock = False #reset flag

    def netinfo(self):
        result={}
        result["body_p"]=self.body
        return json.dumps(result,separators=(',',':')) 
        return result 


class SnakeBlock(pygame.sprite.DirtySprite):
    image = None

    def __init__(self, unit, position, kind, color=(5,113,10)):
        pygame.sprite.DirtySprite.__init__(self)
        self.unit = unit
        self.image = pygame.Surface((self.unit,self.unit))
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*self.unit
        self.rect.y = position[1]*self.unit
        self.dirty = 1
        self.layer = 10
        self.color=color
        self.update_kind(kind, self.color)

    def update_kind(self,kind, mycolor):
        self.kind = kind
        self.dirty = 1

        if self.kind == SnakeBlockKind.HEAD:
            color = (4,80,7)
        elif self.kind == SnakeBlockKind.BODY:
            color = mycolor
        else:
            color = Constants.COLOR_BG

        if self.kind == SnakeBlockKind.NOTHING:
            rect_a = pygame.Rect(0,0,self.unit,self.unit)
            pygame.draw.rect(self.image, color, rect_a)
        else:
            rect_a = pygame.Rect(1,1,self.unit-2,self.unit-2)
            rect_b = pygame.Rect(0,0,self.unit,self.unit)
            pygame.draw.rect(self.image, (100,100,100), rect_b)
            pygame.draw.rect(self.image, color, rect_a)

    def update_color(self,color):
        self.dirty = 1
        if self.kind == SnakeBlockKind.NOTHING:
            rect_a = pygame.Rect(0,0,self.unit,self.unit)
            pygame.draw.rect(self.image, color, rect_a)
        else:
            rect_a = pygame.Rect(1,1,self.unit-2,self.unit-2)
            rect_b = pygame.Rect(0,0,self.unit,self.unit)
            pygame.draw.rect(self.image, (100,100,100), rect_b)
            pygame.draw.rect(self.image, color, rect_a)
        #rect_a = pygame.Rect(0,0,self.unit,self.unit)
        #pygame.draw.rect(self.image, color, rect_a)
