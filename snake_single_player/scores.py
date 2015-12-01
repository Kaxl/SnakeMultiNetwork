#
#  YetAnotherPythonSnake 0.92
#  Author: Simone Cingano (simonecingano@gmail.com)
#  Web: http://simonecingano.it
#  Licence: MIT
#

import pygame
import random

#YASP common imports
from constants import Constants

#YASP imports
from object_snake import SnakeBlock,SnakeBlockKind

def scale(obj,factor=0,height=0,width=0):
    w,h = obj.get_size()

    if factor:
        w,h = (int(w*factor),int(h*factor))
    elif height:
        w = int((height/float(h))*w)
        h = height
    elif width:
        h = int((width/float(w))*h)
        w = width

    return (w,h)

class Score(object):
    def __init__(self,name,color,init_score=0):
        self.name=name
        self.color=color
        self.score=init_score

class Scores(object):
    def __init__(self,size,unit=Constants.RESOLUTION[0]/Constants.UNITS):
        self.unit = unit
        self.image = pygame.Surface(size)
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont("courrier", int(self.unit*2.3))
        self.scores={}

        self.img_logos = pygame.image.load("data/title.png")
        self.img_logos = pygame.transform.smoothscale(self.img_logos,\
                scale(self.img_logos,width=self.unit*10))
        
        self.img_logoh = pygame.image.load("data/hepia.png")
        self.img_logoh = pygame.transform.smoothscale(self.img_logoh,\
                scale(self.img_logoh,width=self.unit*10))
        
        self.img_logo = pygame.image.load("data/iti.png")
        self.img_logo = pygame.transform.smoothscale(self.img_logo,\
                scale(self.img_logo,height=self.unit*25))
        


    def inc_score(self, who, score):
        self.scores[who].score+=score
    
    def set_score(self, who, score):
        self.scores[who].score=score
    
    def del_score(self, name):
        del self.scores[name]
    
    def del_scores(self):
        self.scores={}
    
    def new_score(self, name, color,init_score=0):
        self.scores[name]=Score(name,color,init_score)

    def draw(self,surface):

        self.image.fill((200,200,200))

        pos=0
        for ii in self.scores:
            text_score = str(self.scores[ii].score)
            text_name = ii
            
            sprite = SnakeBlock(self.unit,(1,pos*2+1),SnakeBlockKind.BODY,color=self.scores[ii].color)
            
            text_name = self.font.render(text_name, True, (0,0,0))
            textRectName = text_name.get_rect()
            textRectName.right = self.image.get_rect().right-int(self.unit*5) 
            textRectName.y = int(self.unit*(pos*2+0.6))


            text_score = self.font.render(text_score, True, (0,0,0))
            textRect = text_score.get_rect()
            textRect.right = self.image.get_rect().right-int(self.unit)
            textRect.y = int(self.unit*(pos*2+0.6))
            
            self.image.blit(text_score, textRect)
            self.image.blit(text_name, textRectName)
            self.image.blit(sprite.image, sprite.rect)
            
            self.image.blit(self.img_logos, (self.unit*5,(Constants.UNITS-10)*self.unit))
            self.image.blit(self.img_logoh, (self.unit*4,(Constants.UNITS-3)*self.unit))
            self.image.blit(self.img_logo, (0,(Constants.UNITS-25)*self.unit))
            pos+=1

        surface.blit(self.image,self.rect)
