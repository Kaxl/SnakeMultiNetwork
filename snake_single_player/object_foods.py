#
#  YetAnotherPythonSnake 0.92
#  Author: Simone Cingano (simonecingano@gmail.com)
#  Web: http://simonecingano.it
#  Licence: MIT
#

import pygame
import random
from constants import Constants

class Foods(object):

    def __init__(self, unit=Constants.RESOLUTION[0]/Constants.UNITS):
        self.unit = unit
        self.group = pygame.sprite.LayeredDirty()
        self.refresh = []
        self.positions = []          # food coordinates

    #reset all food positions
    def set_positions(self,positions):
        self.group = pygame.sprite.LayeredDirty()
        self.positions=[]
        for p in positions:
            self.group.add(FoodBlock(self.unit,p))
            self.positions.append(p)

    def make(self):
        position = [random.randint(0,Constants.UNITS-1),random.randint(0,Constants.UNITS-1)]
        while position in self.positions:
            position = [random.randint(0,Constants.UNITS-1),random.randint(0,Constants.UNITS-1)]
        self.group.add(FoodBlock(self.unit,position))
        self.positions.append(position)
        return position

    def collide(self,unit,group,position):
        el = pygame.sprite.Sprite()
        el.rect = pygame.Rect(position[0]*unit,position[1]*unit,unit,unit)
        return pygame.sprite.spritecollide(el, group, False) 

    def check(self,position):
        sprites = self.collide(self.unit,self.group,position)
        for el in sprites:
            self.positions.remove(el.position)
            self.group.remove(el)
            del el
            return True
        return False

    def draw(self,surface):
        self.group.draw(surface)
    
    def netinfo(self):
        return self.positions


class FoodBlock(pygame.sprite.DirtySprite):
    image = None

    def __init__(self, unit, position):
        # self.dirty = 0 means no repainting, 1 repaint and set to 0, 2 repaint every frame
        pygame.sprite.DirtySprite.__init__(self)
        self.unit = unit
        self.image = pygame.Surface((self.unit,self.unit))
        self.position = position
        self.rect = self.image.get_rect()
        self.rect.x = position[0]*self.unit
        self.rect.y = position[1]*self.unit

        color = (184,11,8)
        color2 = (5,113,10)

        self.layer = 10
        self.dirty = 2

        size = int(self.unit*0.8) + 1
        offset = int((self.unit-size)/2)+1
        pygame.draw.rect(self.image, color, (offset,offset, size, size), 0)
        pygame.draw.rect(self.image, color2, (offset*2,0,int(size/3),int(size/2)), 0)
