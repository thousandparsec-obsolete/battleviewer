import pygame, states, math, Numeric, constants

from ocempgui.object import BaseObject

class DamageAnimation (BaseObject, pygame.sprite.Sprite):
    states = states.States('waiting', 'animating', 'finished')
    state = None
    font = None
    
    def __init__ (self, manager, damage_amount, position, animation_duration=0, wait_duration=0, font_path='./fonts/'):
        BaseObject.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        
        if DamageAnimation.font == None:
            # Bitstream Vera Sans Mono
            DamageAnimation.font = pygame.font.Font(font_path+'VeraMoBd.ttf', 18)
        
        if manager:
            self.manager = manager
        
        self.x = position[0]
        self.y = position[1]
        
        shadow_offset = 3
        text = DamageAnimation.font.render(str(int(damage_amount)), False, (255,0,0)).convert()
        shadow = DamageAnimation.font.render(str(int(damage_amount)), False, (50,50,50)).convert()
        self.display_image = pygame.surface.Surface(
            (text.get_width() + shadow_offset,  text.get_height() + shadow_offset), 0, 32).convert_alpha()
        self.display_image.fill((0,0,0,0))
        self.display_image.blit(shadow, (shadow_offset, shadow_offset))
        self.display_image.blit(text, (0, 0))
        self.idle_image = pygame.surface.Surface((0,0))
        self.image = self.idle_image
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

        self.wait_duration = wait_duration
        self.duration = float(animation_duration)
        
        # Record of original alpha for blending
        self.original_alpha = pygame.surfarray.array_alpha(self.display_image)
        
        self.state = self.states.waiting
        self.timestamp = pygame.time.get_ticks()

        self.emit(constants.EVENT_ENTITY_WAIT, self)
 
    def update (self, ticks):
        if self.state == self.states.waiting:
            if ticks > self.timestamp + self.wait_duration:
                self.timestamp = ticks
                self.state = self.states.animating
                self.image = self.display_image
        
        if self.state == self.states.animating:
            distance = 150
            n = min(1, (ticks - self.timestamp) / self.duration)
            self.rect.left = self.x + self.image.get_width() * math.sin(n*10)
            self.rect.top = self.y + (-distance * n)
            
            # Alpha fade
            pygame.surfarray.pixels_alpha(self.image)[:,:] = Numeric.multiply(self.original_alpha, 1-n).astype(Numeric.UInt8)
            
            if n == 1:
                self.emit(constants.EVENT_ANIMATION_DAMAGE_COMPLETE, self)
                self.state = self.states.finished
                # Clean up
                self.emit(constants.EVENT_ENTITY_READY, self)
                self.destroy()
                self.kill()

