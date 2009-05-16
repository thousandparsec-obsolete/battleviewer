import pygame, entities, utility, constants, states

from ocempgui.object import BaseObject

class BattleView (BaseObject):
    verbose = False
    states = states.States('ready', 'waiting')
    
    def __init__ (self, display_surface):
        BaseObject.__init__(self)
        
        # Set up list of signals to listen for
        for signal in (constants.EVENT_ROUND_START,
                        constants.EVENT_MESSAGE,
                        constants.EVENT_ENTITY_NEW,
                        constants.EVENT_ENTITY_WAIT,
                        constants.EVENT_ENTITY_READY,
                        constants.EVENT_BATTLE_START,
                        constants.EVENT_ANIMATION_LASER,
                        constants.EVENT_ANIMATION_DAMAGE):
            self._signals[signal] = []
        
        # Initialize the display
        self.display_surface = display_surface
        
        # Create a background surface
        background_color = (0,0,0)
        self.background_surface = pygame.surface.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        self.background_surface.fill(background_color)
        
        # Create starfield background
        star_count = 200
        utility.static_starfield(self.background_surface, star_count)

        # Blit the background surface to the display surface
        self.display_surface.blit(self.background_surface, (0,0))
    
        # Update the whole display
        pygame.display.flip()
        
        # Sprite group for drawing all messages
        self.message_group = pygame.sprite.RenderUpdates()
        
        # Sprite group for drawing all entities
        self.entity_group = pygame.sprite.RenderUpdates()
        
        # Sprite group for drawing all entities
        self.weapon_group = pygame.sprite.RenderUpdates()
        
        # Sprite group for damage animations
        self.damage_group = pygame.sprite.RenderUpdates()
        
        self.battle_active = False
        
        self.round_timestamp = None
        self.round_delay = 1500 # Should come from config file
        
        # Number of objects who have requested we wait for them before ending the round
        self.waiting_counter = 0

        self.state = BattleView.states.ready
        
    def on_message (self, message):
        if self.verbose: print "'" + str(message) + "'"
        self.message_group.add(entities.Message(self.manager, str(message)))
        
    def on_entity_new (self, entity_instance):
        self.entity_group.add(entity_instance)

    def on_entity_wait (self, entity_ref):
        self.waiting_counter += 1
        
    def on_entity_ready (self, entity_ref):
        self.waiting_counter -= 1
    
    def on_round_start (self):
        self.state = BattleView.states.waiting
        
    def on_battle_start (self):
        # start waiting. must do this first incase on_entity_wait is called
        self.state = BattleView.states.waiting
        self.waiting_counter = 0
        
        # Determin placement of entities and move them
        sides = {}
        for entity in self.entity_group:
            if not sides.has_key(entity.side):
                sides[entity.side] = []
            sides[entity.side].append(entity)
        
        # right now will only work with 2 fleets until a suitable algo is decided upon
        # probably use a circle! send events to your brothers and parents, not to your children!
        
        y_padding = 64
        x_padding = 64
        
        entity_size = 138
        y = y_padding
        for side in sides.values():
            x = x_padding
            for entity in side:
                entity.move((x, y))
                # add warp-in code here
                x += entity_size
            y += self.display_surface.get_height() - (y_padding * 2) - entity_size
        
    def on_start_round (self, data):
        # start waiting. must do this first incase on_entity_wait is called
        self.state = BattleView.states.waiting
        self.waiting_counter = 0
    
    def on_animation_laser (self, animation_instance):
        self.weapon_group.add(animation_instance)
        
    def on_animation_damage (self, animation_instance):
        self.damage_group.add(animation_instance)
        
    def notify (self, event):
        if event.signal == constants.EVENT_ROUND_START:
            self.on_round_start()
        elif event.signal == constants.EVENT_MESSAGE:
            self.on_message(event.data)
        elif event.signal == constants.EVENT_ENTITY_NEW:
            self.on_entity_new(event.data)
        elif event.signal == constants.EVENT_BATTLE_START:
            self.on_battle_start()
        elif event.signal == constants.EVENT_ENTITY_WAIT:
            self.on_entity_wait(event.data)
        elif event.signal == constants.EVENT_ENTITY_READY:
            self.on_entity_ready(event.data)
        elif event.signal == constants.EVENT_ANIMATION_LASER:
            self.on_animation_laser(event.data)
        elif event.signal == constants.EVENT_ANIMATION_DAMAGE:
            self.on_animation_damage(event.data)
            
    def append_round (self, round_label, action_list):
        if self.verbose: print 'Added new round with',len(action_list),'actions.'
        self.round_list.append({'label': round_label, 'actions': action_list})
                
    def update (self):
        # update sprite groups.  waiting_counter will be incrimented here by sprites calling a
        # EVENT_ENTITY_WAIT event and decrimented by an EVENT_ENTITY_READY event
        
        now = pygame.time.get_ticks()
        self.entity_group.update(now)
        self.weapon_group.update(now)
        self.damage_group.update(now)
        self.message_group.update(now)
        
        # Redraw sprites
        rectlist = self.entity_group.draw(self.display_surface)
        rectlist += self.weapon_group.draw(self.display_surface)
        rectlist += self.damage_group.draw(self.display_surface)
        rectlist += self.message_group.draw(self.display_surface)
        
        # Update the surface
        pygame.display.update(rectlist)
        
        # Clear the entities - Would be nice to know of a faster way to do this instead of using 3 seperate commands
        self.entity_group.clear(self.display_surface, self.background_surface)
        self.weapon_group.clear(self.display_surface, self.background_surface)
        self.damage_group.clear(self.display_surface, self.background_surface)
        self.message_group.clear(self.display_surface, self.background_surface)
        
        if self.state == BattleView.states.waiting and self.waiting_counter == 0:
            if self.round_timestamp == None:
                self.round_timestamp = pygame.time.get_ticks() + self.round_delay
            elif self.round_timestamp < pygame.time.get_ticks():
                self.round_timestamp = None
                self.state = BattleView.states.ready
                # not waiting on any sprites. call a EVENT_VIEW_READY so the controller can continue
                self.emit(constants.EVENT_VIEW_READY, None)
