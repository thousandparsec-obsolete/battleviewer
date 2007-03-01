import pygame, weapons, entities, utility, constants

from ocempgui.object import BaseObject

class BattleView (BaseObject):
    verbose = True
    
    def __init__ (self, display_surface):
        BaseObject.__init__(self)
        
        self._signals[constants.EVENT_MESSAGE] = []
        self._signals[constants.EVENT_ENTITY_NEW] = []
        self._signals[constants.EVENT_BATTLE_START] = []
        
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
        
        # Sprite group for drawing all entities
        self.entity_group = pygame.sprite.RenderUpdates()
        
        # Sprite group for drawing all entities
        self.weapon_group = pygame.sprite.RenderUpdates()
        
        # Sprite group for damage animations
        self.damage_group = pygame.sprite.RenderUpdates()
        
        self.battle_active = False
        
        self.round_timestamp = None
        self.round_delay = 1500 # Should come from config file
        
        
    def on_message (self, message):
        print "'" + str(message) + "'"
        
    def on_entity_new (self, entity_instance):
        self.entity_group.add(entity_instance)

    def on_battle_start (self):
        # Determin placement of entities and signal their move
        sides = {}
        for entity in self.entity_group:
            if not sides.has_key(entity.side):
                sides[entity.side] = []
            sides[entity.side].append(entity)
        
        # right now will only work with 2 fleets until a suitable algo is decided upon
        entity_size = 138
        y = 0
        for side in sides.values():
            x = 0
            for entity in side:
                self.emit(constants.EVENT_ENTITY_MOVE, (entity.reference, (x, y)))
                x += entity_size
            y += self.display_surface.get_height() - entity_size
        
    def notify (self, event):
        if event.signal == constants.EVENT_MESSAGE:
            self.on_message(event.data)
        elif event.signal == constants.EVENT_ENTITY_NEW:
            self.on_entity_new(event.data)
        elif event.signal == constants.EVENT_BATTLE_START:
            self.on_battle_start()
            
    def append_round (self, round_label, action_list):
        if self.verbose: print 'Added new round with',len(action_list),'actions.'
        self.round_list.append({'label': round_label, 'actions': action_list})
        
    def next_round (self):
        if self.round == len(self.round_list):
            # Finished all rounds
            self.battle_active = False
            if self.verbose: print 'Battle ended.'
            return
        
        # process actions
        if self.verbose: print 'Starting round',self.round_list[self.round]['label']
        for action in self.round_list[self.round]['actions']:
            # I know isinstance is evil, but it's so useful
            if isinstance(action, actions.Log):
                self.log_message(action.message)
            elif isinstance(action, actions.Move):
                if self.entity_list.has_key(action.reference):
                    self.entity_list[action.reference].move(action.position)
                else:
                    print 'Entity ID',action.reference,'not in entity list.'
            elif isinstance(action, actions.Fire):
                source_position = self.entity_list[action.source_reference].get_position()
                destination_position = self.entity_list[action.destination_reference].get_position()
                if isinstance(self.entity_list[action.source_reference].weapon, weapons.BasicLaser):
                    # laser weapon
                    laser_entity = entities.LaserBlast(self.entity_list[action.source_reference].weapon, source_position, destination_position)
                    self.weapon_group.add(laser_entity)
                else:
                    print 'Warning Unknown weapon', self.entity_list[action.source_reference], self.entity_list[action.source_reference].weapon
            elif isinstance(action, actions.Damage):
                position = self.entity_list[action.reference].get_position()
                damage_animation = entities.DamageAnimation(action.amount, position, 2000, 400)
                self.damage_group.add(damage_animation)
            elif isinstance(action, actions.Death):
                self.entity_group[action.reference].death()
                
        # Incriment the round
        self.round += 1
                
    def update (self):
        # Redraw sprites
        rectlist = self.entity_group.draw(self.display_surface)
        pygame.display.update(rectlist)
        self.entity_group.clear(self.display_surface, self.background_surface)
        
        #~ if not self.battle_active:
            #~ return
        
        #~ # Round completed flag
        #~ complete = True
        
        # Update all sprites - we manually do this so we can determin if all sprites are idle
        #~ for sprite in self.entity_group:
            #~ # Tell the entity to update
            #~ sprite.update(pygame.time.get_ticks())
            #~ if not sprite.is_idle():
                #~ complete = False
        
        #~ # Redraw sprites
        #~ rectlist = self.entity_group.draw(self.display_surface)
        
        #~ pygame.display.update(rectlist)
            
        #~ self.entity_group.clear(self.display_surface, self.background_surface)
        
        #~ if complete:
            #~ if self.round_timestamp == None:
                #~ self.round_timestamp = pygame.time.get_ticks() + self.round_delay
            #~ elif self.round_timestamp < pygame.time.get_ticks():
                #~ self.round_timestamp = None
                #~ self.next_round()