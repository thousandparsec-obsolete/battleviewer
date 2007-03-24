import pygame, states, math, constants, weapons, entities

from ocempgui.object import BaseObject

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
            # temporary until weapon hardpoints work
            spread = 12
            x,y = self.get_position()
            laser_entity0 = entities.LaserBlast(self.manager, self.weapon, (x-spread,y), destination_reference.get_position())
            laser_entity1 = entities.LaserBlast(self.manager, self.weapon, (x+spread,y), destination_reference.get_position())
            self.emit(constants.EVENT_ANIMATION_LASER, laser_entity0)
            self.emit(constants.EVENT_ANIMATION_LASER, laser_entity1)
        else:
            print 'Warning Unknown weapon', self, self.weapon

    def get_position (self):
        return self.rect.center
        
    def on_entity_damage (self, amount):
        entity_instance = entities.DamageAnimation(self.manager, amount, self.get_position(), 2000, 400)
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
        self.emit(constants.EVENT_ENTITY_WAIT, self)
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
                self.emit(constants.EVENT_ENTITY_READY, self)
                self.destroy()
                self.kill()


