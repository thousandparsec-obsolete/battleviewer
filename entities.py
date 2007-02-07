import pygame, states, math, Numeric

# entities and sprites mixed is a bit messy.  this should be cleaned up.

class BasicEntity (pygame.sprite.Sprite):
    side = None
    reference = None
    name = None
    weapon = None
    image = None
    rect = None
    states = states.States('idle', 'death')
    state = None
    
    def __init__ (self, side, reference, name, model, weapon=None, weapon_points=[]):
        pygame.sprite.Sprite.__init__(self)
        self.side = side
        self.reference = reference
        self.name = name
        self.weapon = weapon
        self.weapon_points = weapon_points
        
        self.state = self.states.idle
        
        self.death_duration = 1500.0
        
        # Probably want to consider converting these
        self.display_image = pygame.image.load(model)
        self.idle_image = pygame.surface.Surface((0,0))
        
        self.image = self.idle_image
        
        self.rect = pygame.rect.Rect(0, 0, self.image.get_width(), self.image.get_height())
        
    def death (self):
        # copy the display image so we can mess with it in the death animation
        self.image = self.display_image.copy()
        self.timestamp = pygame.time.get_ticks()
        # Play fancy kill animation!
        self.state = self.states.death
        
    def move (self, position):
        # Change to display image now we have a valid position
        self.image = self.display_image
        self.rect = pygame.rect.Rect(0, 0, self.image.get_width(), self.image.get_height())
        # Update our rect position
        self.rect.move_ip(position[0], position[1])
        
    def update (self):
        if self.state == self.states.death:
            n = min(1, (pygame.time.get_ticks() - self.timestamp) / self.death_duration)
            # We can destroy this since this is the final use of this entities image
            pygame.surfarray.pixels3d(self.image)[:,:,0] = 126 + 126 * math.cos(n*24)
            if n == 1:
                self.image = self.idle_image
                self.state = self.states.idle
                self.kill()
            
    def get_position (self):
        return self.rect.center
        
    def is_idle (self):
        return ( self.state == self.states.idle )

class DamageAnimation (pygame.sprite.Sprite):
    position = None
    timestamp = 0
    duration = 0
    wait_duration = 0
    states = states.States('waiting', 'animating', 'finished')
    state = None
    font = None
    
    def __init__ (self, damage_amount, position, animation_duration=0, wait_duration=0):
        pygame.sprite.Sprite.__init__(self)
        
        if DamageAnimation.font == None:
            # Bitstream Vera Sans Mono
            DamageAnimation.font = pygame.font.Font('./fonts/VeraMoBd.ttf', 18)
            
        self.x = position[0]
        self.y = position[1]
        
        shadow_offset = 3
        text = self.font.render(str(int(damage_amount)), False, (255,0,0)).convert()
        shadow = self.font.render(str(int(damage_amount)), False, (50,50,50)).convert()
        self.display_image = pygame.surface.Surface((text.get_width() + shadow_offset,  text.get_height() + shadow_offset), 0, 32).convert_alpha()
        self.display_image.fill((0,0,0,0))
        self.display_image.blit(shadow, (shadow_offset, shadow_offset))
        self.display_image.blit(text, (0, 0))
        self.idle_image = pygame.surface.Surface((0,0))
        self.image = self.idle_image
        self.rect = pygame.rect.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())
        
        # Record of original alpha for blending
        self.original_alpha = pygame.surfarray.array_alpha(self.display_image)
        
        self.state = self.states.waiting
        self.wait_duration = wait_duration
        self.duration = float(animation_duration)
        self.timestamp = pygame.time.get_ticks()
        
    def is_idle (self):
        return ( self.state == self.states.finished )
        
    def update (self):
        if self.state == self.states.waiting:
            if pygame.time.get_ticks() > self.timestamp + self.wait_duration:
                self.timestamp = pygame.time.get_ticks()
                self.state = self.states.animating
                self.image = self.display_image
        if self.state == self.states.animating:
            distance = 150
            n = min(1, (pygame.time.get_ticks() - self.timestamp) / self.duration)
            self.rect.left = self.x + self.image.get_width() * math.sin(n*10)
            self.rect.top = self.y + (-distance * n)
            
            # Alpha fade
            pygame.surfarray.pixels_alpha(self.image)[:,:] = Numeric.multiply(self.original_alpha, 1-n).astype(Numeric.UInt8)
            
            if n == 1:
                self.state = self.states.finished
                self.kill()
        
class LaserBlast (pygame.sprite.Sprite):
    weapon = None
    image = None
    rect = None
    duration = 0
    timestamp = 0
    states = states.States('idle', 'animating')
    state = None
    
    def __init__ (self, weapon, source_position, destination_position):
        pygame.sprite.Sprite.__init__(self)
        self.weapon = weapon
        
        width = destination_position[0] - source_position[0]
        height = destination_position[1] - source_position[1]
        
        x = source_position[0]
        y = source_position[1]
        
        if width < 0:
            width = abs(width)
            x = destination_position[0]
        if height < 0:
            height = abs(height)
            y = destination_position[1]
        
        self.margin = 10
        width += self.margin * 2
        height += self.margin * 2
        
        self.image = pygame.surface.Surface((width, height), 0, 32)
        self.rect = pygame.rect.Rect(x-self.margin, y-self.margin, width, height)
        
        self.duration = float(self.weapon.duration)
        self.start_animation()
        
    def start_animation (self):
        self.image.fill((0,0,0))
        self.image.set_colorkey((0,0,0))
        self.timestamp = pygame.time.get_ticks()
        self.state = self.states.animating
        
    def update (self):
        n = min(1, (pygame.time.get_ticks() - self.timestamp) / self.duration)
        # Should really use an alpha for this
        a = 0.5 + (0.5 * math.sin(n*self.weapon.pulse))
        c = (self.weapon.color[0]*a, self.weapon.color[1]*a, self.weapon.color[2]*a)
        pygame.draw.line(self.image, c, (self.margin,self.margin), (self.image.get_width()-self.margin, self.image.get_height()-self.margin), self.weapon.width)
        if n == 1:
            self.state = self.states.idle
            self.kill()
            
    def is_idle (self):
        return ( self.state == self.states.idle )
