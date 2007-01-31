import pygame, states, math

# entities and sprites mixed is a bit messy.  this should be cleaned up.

class BasicEntity (pygame.sprite.Sprite):
    side = None
    id = None
    name = None
    weapon = None
    image = None
    rect = None
    
    def __init__ (self, side, id, name, model, weapon=None):
        pygame.sprite.Sprite.__init__(self)
        self.side = side
        self.id = id
        self.name = name
        self.weapon = weapon
        
        # Probably want to consider converting these
        self.image = pygame.image.load(model)
        
        # TODO: Need to find a cleaner way of not drawing a sprite.  Current method is dirty!
        self.rect = pygame.rect.Rect(0, 0, self.image.get_width(), self.image.get_height())
        
    def move (self, position):
        self.rect.move_ip(position[0], position[1])
        
    def update (self):
        pass
        
    def get_position (self):
        return self.rect.center
        
    def is_idle (self):
        return True
        
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
