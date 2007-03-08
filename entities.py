import pygame, states, math, Numeric, utility, constants

from ocempgui.object import BaseObject

# entities and sprites mixed is a bit messy.  this should be cleaned up.

class BasicEntity (BaseObject, pygame.sprite.Sprite):
    states = states.States('idle', 'death')
    state = None
    
    def __init__ (self, side, reference, name, model, weapon=None, weapon_points=[]):
        BaseObject.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        
        self.side = side
        self.reference = reference
        self.name = name
        self.weapon = weapon
        self.weapon_points = weapon_points
        
        self.death_duration = 1500.0
        
        self.image = pygame.image.load(model)
        self.rect = pygame.rect.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.state = self.states.idle
        
        self.framecount = 0
        self.frameskip = 3
        
    def move (self, position):
        # Update our rect position
        self.rect.move_ip(position[0], position[1])
        
    #~ def notify (self, event):
        #~ pass
            
    def death (self):
        self.timestamp = pygame.time.get_ticks()
        # Play fancy kill animation!
        self.state = self.states.death

    def update (self, ticks):
        if self.state == self.states.death:
            self.framecount += 1
            if self.framecount < self.frameskip:
                return
            self.framecount = 0
            n = min(1, (ticks - self.timestamp) / self.death_duration)
            # We can destroy this since this is the final use of this entities image
            pygame.surfarray.pixels3d(self.image)[:,:,0] = 126 + 126 * math.cos(n*24)
            if n == 1:
                self.visible = False
                self.state = self.states.idle
                self.kill()
            
    def get_position (self):
        return self.rect.center
        
    def is_idle (self):
        return ( self.state == self.states.idle )

class DamageAnimation (pygame.sprite.Sprite):
    states = states.States('waiting', 'animating', 'finished')
    state = None
    font = None
    
    def __init__ (self, damage_amount, position, animation_duration=0, wait_duration=0, font_path='./fonts/'):
        pygame.sprite.Sprite.__init__(self)
        
        if DamageAnimation.font == None:
            # Bitstream Vera Sans Mono
            DamageAnimation.font = pygame.font.Font(font_path+'VeraMoBd.ttf', 18)
            
        self.x = position[0]
        self.y = position[1]
        
        shadow_offset = 3
        text = self.font.render(str(int(damage_amount)), False, (255,255,255)).convert()
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
                self.state = self.states.finished
                self.kill()

class LaserBlast (pygame.sprite.Sprite):
    states = states.States('idle', 'animating')
    state = None
    
    def __init__ (self, weapon, source_position, destination_position):
        pygame.sprite.Sprite.__init__(self)
        
        self.weapon = weapon
        self.weapon.duration = float(self.weapon.duration) # ensure we are using floats
        self.padding = self.weapon.width
        
        self.source_position = source_position
        self.destination_position = destination_position
        
        self.idle_image = pygame.surface.Surface((0,0))
        self.image = self.idle_image
        self.rect = pygame.rect.Rect(self.source_position[0], self.source_position[1], self.image.get_width(), self.image.get_height())
        
        self.framecount = 0
        self.frameskip = 2
        
        # Prerender the laser
        self.draw_laser()
        
        # Start animation
        self.start_animation()
        
    def is_idle (self):
        return ( self.state == self.states.idle )

    def draw_laser (self):
        
        # determin width
        xwidth = (self.destination_position[0] - self.source_position[0])
        ywidth = (self.destination_position[1] - self.source_position[1])
        
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
        tmp_image = pygame.surface.Surface((abs(xwidth), abs(ywidth))).convert_alpha()
        tmp_image.fill((0,0,0))
        
        self.laser_rect = tmp_image.get_rect()
        
        # reorganise position variables depending on which quater we are in, also update our rect
        if xwidth > 0:
            if ywidth > 0:
                pos0 = [self.padding, self.padding]
                pos1 = [self.laser_rect.width - self.padding, self.laser_rect.height - self.padding]
                self.laser_rect.move_ip((self.source_position[0] - self.padding, self.source_position[1] - self.padding))
            else:
                pos0 = [self.laser_rect.width - self.padding, self.padding]
                pos1 = [self.padding, self.laser_rect.height - self.padding]
                self.laser_rect.move_ip((self.source_position[0] - self.padding, self.destination_position[1] - self.padding))
        else:
            if ywidth > 0:
                pos0 = [self.laser_rect.width - self.padding, self.padding]
                pos1 = [self.padding, self.laser_rect.height - self.padding]
                self.laser_rect.move_ip((self.destination_position[0] - self.padding, self.source_position[1] - self.padding))
            else:
                pos0 = [self.padding, self.padding]
                pos1 = [self.laser_rect.width - self.padding, self.laser_rect.height - self.padding]
                self.laser_rect.move_ip((self.destination_position[0] - self.padding, self.destination_position[1] - self.padding))
        
        # Draw laser
        pygame.draw.line(tmp_image, (255,255,255), pos0, (pos1[0],pos1[1]), self.weapon.width)
        
        # Blur surface (this will be a gaussian blur later and facilitate a less-poor looking beam)
        utility.blur_surface(tmp_image)
        utility.blur_surface(tmp_image)
        utility.blur_surface(tmp_image)
        
        tmp_array = pygame.surfarray.array3d(tmp_image)
        
        self.laser_image = tmp_image
        self.laser_image.fill(self.weapon.color)
        
        # cheap gradient, need to change this into a LUT of some kind
        w = self.weapon.width
        tm = (255/w)
        color = (self.weapon.color[0], self.weapon.color[1], self.weapon.color[2])
        while w > 0:
            color = (
                min(255, color[0]+tm),
                min(255, color[1]+tm),
                min(255, color[2]+tm))
            pygame.draw.line(self.laser_image, color, pos0, (pos1[0],pos1[1]), w)
            w -= 1
        
        pygame.surfarray.pixels_alpha(self.laser_image)[:,:] = tmp_array[:,:,0]

        # Record of original alpha for blending
        self.laser_alpha = pygame.surfarray.array_alpha(self.laser_image.copy().convert_alpha())
        
        #print self.laser_alpha, self.laser_image, self.laser_rect
        
    def start_animation (self):
        self.current_pulse = 0
        self.image = self.laser_image
        self.rect = self.laser_rect
        self.timestamp = pygame.time.get_ticks()
        self.state = self.states.animating
        
    def update (self, ticks):
        if self.state == self.states.animating:
            self.framecount += 1
            if self.framecount < self.frameskip:
                return
            self.framecount = 0
            n = min(1, (ticks - self.timestamp) / self.weapon.duration)
            # Alpha fade
            pygame.surfarray.pixels_alpha(self.image)[:,:] = Numeric.multiply(self.laser_alpha, 1-n).astype(Numeric.UInt8)
            if n == 1:
                # Loop
                if self.current_pulse < self.weapon.pulse:
                    self.current_pulse += 1
                    self.timestamp = ticks
                else:
                    self.state = self.states.idle
