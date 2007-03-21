import pygame, states, math, Numeric, utility, constants, weapons

from ocempgui.object import BaseObject, ActionListener

# entities and sprites mixed is a bit messy.  this should be cleaned up.

class BasicEntity (BaseObject, pygame.sprite.Sprite):
    states = states.States('idle', 'death')
    state = None
    
    def __init__ (self, manager, side, reference, name, model, weapon=None, weapon_points=[]):
        
        BaseObject.__init__(self)
        pygame.sprite.Sprite.__init__(self)
        
        self._signals[constants.EVENT_ENTITY_FIRE] = []
        self._signals[constants.EVENT_ENTITY_DAMAGE] = []
        self._signals[constants.EVENT_ENTITY_DEATH] = []
        
        self._signals[constants.EVENT_ANIMATION_DAMAGE_COMPLETE] = []
        
        self.manager = manager
        
        self.side = side
        self.reference = reference
        self.name = name
        self.weapon = weapon
        self.weapon_points = weapon_points
        
        self.damage_animation_queue = []
        
        self.death_duration = 1500.0
        
        self.image = pygame.image.load(model)
        self.rect = pygame.rect.Rect(0, 0, self.image.get_width(), self.image.get_height())
        self.state = self.states.idle
        
        self.framecount = 0
        self.frameskip = 3
        
    def on_entity_fire (self, destination_reference):
        if isinstance(self.weapon, weapons.BasicLaser):
            # laser weapon
            laser_entity = LaserBlast(self.manager, self.weapon, self.get_position(), destination_reference.get_position())
            self.emit(constants.EVENT_ANIMATION_LASER, laser_entity)
        else:
            print 'Warning Unknown weapon', self, self.weapon

    def get_position (self):
        return self.rect.center
        
    def on_entity_damage (self, amount):
        entity_instance = DamageAnimation(self.manager, amount, self.get_position(), 2000, 400)
        self.damage_animation_queue.append(entity_instance)
        if len(self.damage_animation_queue) == 1:
            # Tell view to add this animation instance
            self.emit(constants.EVENT_ANIMATION_DAMAGE, (entity_instance))
       
    def on_animation_damage_complete (self, animation_reference):
        if self.damage_animation_queue and id(animation_reference) == id(self.damage_animation_queue[0]):
            self.damage_animation_queue = self.damage_animation_queue[1:]
            if len(self.damage_animation_queue) > 0:
                # Trigger next animation
                self.emit(constants.EVENT_ANIMATION_DAMAGE, self.damage_animation_queue[0])
        
    def on_entity_death (self):
        self.death()
        
    def notify (self, event):
        if event.signal == constants.EVENT_ENTITY_FIRE:
            if event.data[0] == self.reference:
                self.on_entity_fire(event.data[1])
        elif event.signal == constants.EVENT_ENTITY_DAMAGE:
            if event.data[0] == self.reference:
                self.on_entity_damage(event.data[1])
        elif event.signal == constants.EVENT_ANIMATION_DAMAGE_COMPLETE:
            # identify if it is our event inside callback
            self.on_animation_damage_complete(event.data)
        elif event.signal == constants.EVENT_ENTITY_DEATH:
            if event.data == self.reference:
                self.on_entity_death()
                
    def move (self, position):
        # Update our rect position
        self.rect.move_ip(position[0], position[1])
        
    def death (self):
        self.emit(constants.EVENT_ENTITY_WAIT, 0)
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
                # Clean up - This may need to be changed a bit
                self.emit(constants.EVENT_ENTITY_READY, 0)
                self.destroy()
                self.kill()

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
            Message.font = pygame.font.Font(font_path+'VeraMoBd.ttf', 18)
            
        # Increment the number of messages being displayed
        if Message.message_count == None:
            Message.message_count = 0
        else:
            Message.message_count += 1
            
        # Basically a duplication of damage animation - damage animation should probably be derived from this
        self.manager = manager
        
        shadow_offset = 3
        text = Message.font.render(message, False, (200,200,200)).convert()
        shadow = Message.font.render(message, False, (50,50,50)).convert()
        
        self.image = pygame.surface.Surface(
            (text.get_width() + shadow_offset,  text.get_height() + shadow_offset), 0, 32).convert_alpha()
        self.image.fill((0,0,0,0))
        self.image.blit(shadow, (shadow_offset, shadow_offset))
        self.image.blit(text, (0, 0))
        
        display_geometery = pygame.display.get_surface().get_rect()
        x = (display_geometery.width - self.image.get_width()) / 2
        y = (display_geometery.height - self.image.get_height()) / 2 + (self.image.get_height() * Message.message_count-1)
        
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

        self.emit(constants.EVENT_ENTITY_WAIT, 0)
 
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
                self.emit(constants.EVENT_ENTITY_READY, 0)
                self.destroy()
                self.kill()

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
        
        self.emit(constants.EVENT_ENTITY_WAIT, 0)

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
                    self.emit(constants.EVENT_ENTITY_READY, 0)
                    self.destroy()
                    self.kill()
