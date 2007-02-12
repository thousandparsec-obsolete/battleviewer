import pygame, Numeric, math, states

pygame.display.init()

background = pygame.image.load('./background.png')

display = pygame.display.set_mode((background.get_width(),background.get_height()),0,32)
display.blit(background, (0,0))

pygame.display.flip()

class EntitySprite (pygame.sprite.Sprite):
    def __init__ (self, offset):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./minisec/frigate/model.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.offset = offset
        self.rect.left = display.get_width() * 0.5 + 150 * math.cos(self.offset) - self.image.get_width() * 0.5
        self.rect.top = display.get_height() * 0.5 + 100 * math.sin(self.offset) - self.image.get_height() * 0.5
        
    def update (self, ticks):
        # update entity values
        n = ticks / 1000.0
        self.rect.left = display.get_width() * 0.5 + 150 * math.cos(n+self.offset) - self.image.get_width() * 0.5
        self.rect.top = display.get_height() * 0.5 + 100 * math.sin(n+self.offset) - self.image.get_height() * 0.5
        r = pygame.rect.Rect((self.rect.center[0]-1-self.rect.left,self.rect.center[1]-1-self.rect.top), (4,4))
        pygame.draw.rect(self.image, (255,0,0), r, 0)
        
class LaserSprite (pygame.sprite.Sprite):
    states = states.States('idle', 'active')
    state = None
    
    def __init__ (self):
        pygame.sprite.Sprite.__init__(self)
        self.idle_image = pygame.surface.Surface((0,0))
        self.weapon_thickness = 3
        self.padding = self.weapon_thickness
        self.fire_halt()
        
    def fire_halt (self):
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.state = self.states.idle
        
    def fire (self, p0, p1):
        
        xwidth = (p1[0] - p0[0])
        ywidth = (p1[1] - p0[1])
        
        if xwidth < 0:
            xwidth -= self.padding * 2
        else:
            xwidth += self.padding * 2
            
        if ywidth < 0:
            ywidth -= self.padding * 2
        else:
            ywidth += self.padding * 2
            
        self.active_image = pygame.surface.Surface((abs(xwidth), abs(ywidth)))
        self.active_image.fill((0,0,0))
        
        self.image = self.active_image
        self.rect = self.image.get_rect()
        
        if xwidth > 0:
            if ywidth > 0:
                pos0 = [self.padding, self.padding]
                pos1 = [self.rect.width - self.padding, self.rect.height - self.padding]
                self.rect.move_ip((p0[0] - self.padding, p0[1] - self.padding))
            else:
                pos0 = [self.rect.width - self.padding, self.padding]
                pos1 = [self.padding, self.rect.height - self.padding]
                self.rect.move_ip((p0[0] - self.padding, p1[1] - self.padding))
        else:
            if ywidth > 0:
                pos0 = [self.rect.width - self.padding, self.padding]
                pos1 = [self.padding, self.rect.height - self.padding]
                self.rect.move_ip((p1[0] - self.padding, p0[1] - self.padding))
            else:
                pos0 = [self.padding, self.padding]
                pos1 = [self.rect.width - self.padding, self.rect.height - self.padding]
                self.rect.move_ip((p1[0] - self.padding, p1[1] - self.padding))
            
        #~ maskimage = pygame.surface.Surface((self.active_image.width, self.active_image.height))
        pygame.draw.line(self.image, (255,255,255), pos0, pos1, self.weapon_thickness)
        
        rgbarray = pygame.surfarray.array3d(self.image)
        
        soften = Numeric.array(rgbarray).astype(Numeric.Int)
        
        soften[1:,:] += rgbarray[:-1,:]*8
        soften[:-1,:] += rgbarray[1:,:]*8
        soften[:,1:]  += rgbarray[:,:-1]*8
        soften[:,:-1] += rgbarray[:,1:]*8
        soften /= 33
        
        #~ canvasregion_sa = pygame.surfarray.array3d(canvasregion)
        #~ rgbarray[...,0] = Numeric.where(soften[...,0], rgbarray[...,0], 0)
                
        #~ del rgbarray
        
        pygame.surfarray.blit_array(self.image, soften)

        #~ pygame.draw.line(self.image, (255,0, 0),
            #~ (self.padding, self.padding), (self.rect.width-self.padding, self.rect.height-self.padding), 2)
            
        #~ pygame.draw.line(self.image, (255,0, 0),
            #~ (self.rect.width-self.padding, self.padding), (self.padding, self.rect.height-self.padding), 2)
            
        self.state = self.states.active
        
    def update (self, ticks):
        #~ self.rect.move_ip(-self.padding, -self.padding)
        pass
        
e0 = EntitySprite(0)
e1 = EntitySprite(math.pi*1.5)
l0 = LaserSprite()

group = pygame.sprite.OrderedUpdates()

group.add(e0)
group.add(e1)
group.add(l0)

linearea = None

n = 0

clock = pygame.time.Clock()
loop = True
while loop:
    # process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYUP:
            loop = False
        #~ if event.type == pygame.MOUSEMOTION:
            #~ n += 1
            #~ group.update(n)
            #~ l0.fire(e0.rect.center, e1.rect.center)
            
    group.update(pygame.time.get_ticks())
    l0.fire(e0.rect.center, e1.rect.center)
            
    group.clear(display, background)
    
    updatelist = group.draw(display)

    pygame.display.update(updatelist)
    
    clock.tick(25)
