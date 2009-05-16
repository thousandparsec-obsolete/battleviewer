import pygame, states, math, Numeric, utility, constants, weapons

from ocempgui.object import BaseObject

class Message (BaseObject, pygame.sprite.Sprite):
    font = None
    states = states.States('displaying', 'finished')
    state = None
    message_count = None
    verticle_padding = 5
    
    def __init__ (self, manager, message, display_duration=3500, font_path='./fonts/'):
        BaseObject.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        
        if Message.font == None:
            # Bitstream Vera Sans Mono
            Message.font = pygame.font.Font(font_path+'VeraMoBd.ttf', 12)
            
        # Increment the number of messages being displayed
        if Message.message_count == None:
            Message.message_count = 0
        else:
            Message.message_count += 1
            
        # Basically a duplication of damage animation - damage animation should probably be derived from this
        self.manager = manager
        
        shadow_offset = 3
        text = Message.font.render(message, True, (200,200,200)).convert_alpha()
        shadow = Message.font.render(message, True, (50,50,50)).convert_alpha()
        
        self.image = pygame.surface.Surface(
            (text.get_width() + shadow_offset,  text.get_height() + shadow_offset), 0, 32).convert_alpha()
        self.image.fill((0,0,0,0))
        self.image.blit(shadow, (shadow_offset, shadow_offset))
        self.image.blit(text, (0, 0))
        
        display_geometery = pygame.display.get_surface().get_rect()
        x = (display_geometery.width - self.image.get_width()) / 2
        y = (display_geometery.height - self.image.get_height()) / 2 + (self.image.get_height() * (Message.message_count-1))
        
        self.rect = pygame.rect.Rect(x, y, self.image.get_width(), self.image.get_height())
        
        self.display_duration = float(display_duration)        
        self.state = self.states.displaying
        
        self.timestamp = pygame.time.get_ticks()

        self.emit(constants.EVENT_ENTITY_WAIT, 0)
        
    def update (self, ticks):
        if self.state == self.states.displaying:
            if ticks > self.timestamp + self.display_duration:
                self.state = self.states.finished
                # Decrement the number of messages being displayed
                Message.message_count -= 1
                # Clean up
                self.emit(constants.EVENT_ENTITY_READY, 0)
                self.destroy()
                self.kill()
 
