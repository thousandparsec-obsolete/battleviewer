import pygame

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
        print 'Moving entity',self.id,'to position',position
        self.rect.move_ip(position[0], position[1])
        
    def update (self):
        pass
        
    def is_idle (self):
        return True