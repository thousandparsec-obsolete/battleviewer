import pygame, states, Numeric, utility, constants

from ocempgui.object import BaseObject

class LaserBlast (BaseObject, pygame.sprite.Sprite):
    states = states.States('idle', 'animating')
    state = None
    
    def __init__ (self, manager, weapon, source_position, destination_position):
        BaseObject.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        
        self.manager = manager
        
        self.weapon = weapon
        self.weapon.duration = float(self.weapon.duration) # ensure we are using floats
        self.padding = self.weapon.width
        
        self.source_position = source_position
        self.destination_position = destination_position
        
        self.idle_image = pygame.surface.Surface((0,0))
        self.image = self.idle_image
        self.rect = pygame.rect.Rect(
            self.source_position[0], self.source_position[1], self.image.get_width(), self.image.get_height())
        
        self.framecount = 0
        self.frameskip = 2
        
        # Prerender the laser
        self.draw_laser()
        
        # Start animation
        self.current_pulse = 0
        self.image = self.laser_image
        self.rect = self.laser_rect
        self.timestamp = pygame.time.get_ticks()
        self.state = self.states.animating
        
        self.emit(constants.EVENT_ENTITY_WAIT, self)

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
                    # Complete animation
                    self.state = self.states.idle
                    # Clean up
                    self.emit(constants.EVENT_ENTITY_READY, self)
                    self.destroy()
                    self.kill()

