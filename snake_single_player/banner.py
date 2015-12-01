import pygame
from constants import Constants

class Banner(object):
        def __init__(self, unit=Constants.RESOLUTION[0]/Constants.UNITS):
       
            self.unit = unit
            self.image = pygame.Surface((self.unit*10,self.unit*2))
            self.font = pygame.font.SysFont("courrier", int(self.unit*2.3))
            self.color=self.current_color=(255,0,0)
			
        def blink(self):
            if self.current_color == self.color:
                self.current_color=(0,0,0)
            elif self.current_color == (0,0,0):
                self.current_color=self.color

        def blank(self,surface):
            self.image.fill(Constants.COLOR_BG)
            
        def draw_connecting(self,surface,where):
            text = self.font.render("Connecting...", True, self.current_color)
            self.image.blit(text,(0,0))
            surface.blit(self.image,where)
