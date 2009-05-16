import pygame, states, math, numeric, utility, constants, weapons

from ocempgui.object import BaseObject

class SummaryScreen (BaseObject, pygame.sprite.Sprite):
    font = None
    
    def __init__ (self, manager, font_path='./fonts/'):
        BaseObject.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        
        if SummaryScreen.font == None:
            # Bitstream Vera Sans Mono
            SummaryScreen.font = pygame.font.Font(font_path+'VeraMoBd.ttf', 12)
            
        # Basically a duplication of damage animation - damage animation should probably be derived from this
        self.manager = manager
        
    def update (self, ticks):
        pass

