import pygame, Numeric, math, states, random

def blur_surface (rgb_surface):
    # Basic averaging blur
    array_rgb = pygame.surfarray.array3d(rgb_surface)
    array_soften = Numeric.array(array_rgb).astype(Numeric.Int)
    array_soften[1:,:] += array_rgb[:-1,:]*8
    array_soften[:-1,:] += array_rgb[1:,:]*8
    array_soften[:,1:]  += array_rgb[:,:-1]*8
    array_soften[:,:-1] += array_rgb[:,1:]*8
    array_soften /= 33
    pygame.surfarray.blit_array(rgb_surface, array_soften)
    
class EntitySprite (pygame.sprite.Sprite):
    def __init__ (self, offset, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./minisec/frigate/model.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.offset = offset
        self.color = color
        #~ self.rect.left = display.get_width() * 0.5 + 150 * math.cos(self.offset) - self.image.get_width() * 0.5
        #~ self.rect.top = display.get_height() * 0.5 + 100 * math.sin(self.offset) - self.image.get_height() * 0.5
        self.rect.left = ( display.get_width() - self.image.get_width() ) * random.random()
        self.rect.top =  ( display.get_height() - self.image.get_height() ) * random.random()
        
    def update (self, ticks):
        # update entity values
        n = ticks / 5000.0
        #~ self.rect.left = display.get_width() * 0.5 + 150 * math.cos(n+self.offset) - self.image.get_width() * 0.5
        #~ self.rect.top = display.get_height() * 0.5 + 100 * math.sin(n+self.offset) - self.image.get_height() * 0.5
        #~ r = pygame.rect.Rect((self.rect.center[0]-1-self.rect.left,self.rect.center[1]-1-self.rect.top), (4,4))
        #~ pygame.draw.rect(self.image, self.color, r, 0)
        
class LaserSprite (pygame.sprite.Sprite):
    states = states.States('idle', 'active')
    state = None
    
    def __init__ (self, laser_color=(255,255,255), width=1, duration=150.0, repeat=1):
        pygame.sprite.Sprite.__init__(self)
        self.laser_color = laser_color
        self.weapon_thickness = width
        self.padding = self.weapon_thickness
        self.idle_image = pygame.surface.Surface((0,0))
        self.original_alpha = None
        self.duration = float(duration)
        self.repeats = repeat
        self.current_repeat = 0
        self.timestamp = 0
        self.fire_halt()
        
    def fire_halt (self):
        self.image = self.idle_image
        self.rect = self.image.get_rect()
        self.state = self.states.idle
        self.original_alpha = None
        
    def draw_laser (self, p0, p1):
        
        # determin width
        xwidth = (p1[0] - p0[0])
        ywidth = (p1[1] - p0[1])
        
        # alter width for padding
        if xwidth < 0:
            xwidth -= self.padding * 2
        else:
            xwidth += self.padding * 2
            
        if ywidth < 0:
            ywidth -= self.padding * 2
        else:
            ywidth += self.padding * 2
        
        # Create the laser alpha channel surface
        mask_image = pygame.surface.Surface((abs(xwidth), abs(ywidth))).convert_alpha()
        mask_image.fill((0,0,0))
        
        self.rect = mask_image.get_rect()
        
        # reorganise position variables depending on which quater we are in, also update our rect
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
        
        # Draw laser
        pygame.draw.line(mask_image, (255,255,255), pos0, (pos1[0],pos1[1]), self.weapon_thickness)
        
        
        # Blur surface (this will be a gaussian blur later and facilitate a less-poor looking beam)
        blur_surface(mask_image)
        blur_surface(mask_image)
        blur_surface(mask_image)
        
        mask_array = pygame.surfarray.array3d(mask_image)
        
        self.image = mask_image
        self.image.fill(self.laser_color)
        
        # cheap gradient
        w = self.weapon_thickness
        tm = (255/self.weapon_thickness)
        color = (self.laser_color[0], self.laser_color[1], self.laser_color[2])
        while w > 0:
            color = (
                min(255, color[0]+tm),
                min(255, color[1]+tm),
                min(255, color[2]+tm))
            pygame.draw.line(self.image, color, pos0, (pos1[0],pos1[1]), w)
            w -= 1
        
        pygame.surfarray.pixels_alpha(self.image)[:,:] = mask_array[:,:,0]

        # Record of original alpha for blending
        self.original_alpha = pygame.surfarray.array_alpha(self.image.copy().convert_alpha())
        
        self.timestamp = pygame.time.get_ticks()
        
        self.state = self.states.active
        
    def update (self, ticks):
        if self.original_alpha != None:
            n = min(1, (ticks - self.timestamp) / self.duration)
            # Alpha fade
            pygame.surfarray.pixels_alpha(self.image)[:,:] = Numeric.multiply(self.original_alpha, 1-n).astype(Numeric.UInt8)
            if n == 1:
                # Loop
                if self.current_repeat < self.repeats:
                    self.current_repeat + 1
                    self.timestamp = pygame.time.get_ticks()

# Main test
pygame.display.init()

background = pygame.image.load('./background.png')
background.fill((0,0,0))

# Cheesy stars
starcount = 200
for n in range(starcount):
    r = random.randrange(100,255)
    color = (r,r,r)
    background.set_at((random.randrange(0, background.get_width()), random.randrange(0, background.get_height())), color)

# Cheesy blur
blur_surface(background)

display = pygame.display.set_mode((background.get_width(),background.get_height()),0,32)
display.blit(background, (0,0))

pygame.display.flip()
            
e0 = EntitySprite(0, (255,0,0))
e1 = EntitySprite(math.pi*1.5, (0,255,0))
l0 = LaserSprite((128,0,255), 3, 200, 1)
l1 = LaserSprite((255,255,0), 5, 1000, 1)
group = pygame.sprite.OrderedUpdates()

group.add(e0)
group.add(e1)
group.add(l1)
group.add(l0)

linearea = None

n = 0

clock = pygame.time.Clock()
loop = True

area = 20
target1 = (e1.rect.center[0] + random.randrange(-area,area), e1.rect.center[1] + random.randrange(-area,area))
target0 = (e0.rect.center[0] + random.randrange(-area,area), e0.rect.center[1] + random.randrange(-area,area))
        
timer = 0

while loop:
    # process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYUP:
            loop = False
            
    if timer < pygame.time.get_ticks():
        target1 = (e1.rect.center[0] + random.randrange(-area,area), e1.rect.center[1] + random.randrange(-area,area))
        target0 = (e0.rect.center[0] + random.randrange(-area,area), e0.rect.center[1] + random.randrange(-area,area))
        timer = pygame.time.get_ticks() + 250
        l0.draw_laser(e0.rect.center, target1)
        l1.draw_laser(e1.rect.center, target0)
        
    
    group.update(pygame.time.get_ticks())
    
    group.clear(display, background)
    
    updatelist = group.draw(display)

    pygame.display.update(updatelist)
    
    clock.tick(25)
