import pygame, actions, weapons, entities

class BattleView:
    # Reference to the pygame display surface
    display_surface = None
    background_surface = None
    entity_list = None
    round = 0
    round_list = None
    battle_active = False
    spritegroup = None
    verbose = True
    round_timestamp = None
    round_delay = 1500
    
    def __init__ (self, display_surface):
        # Initialize the display
        self.display_surface = display_surface
        
        # Create a background surface
        background_color = (0,0,0)
        self.background_surface = pygame.surface.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        self.background_surface.fill(background_color)
        
        # Blit the background surface to the display surface
        self.display_surface.blit(self.background_surface, (0,0))
    
        # Update the whole display
        pygame.display.flip()
        
        # List to contain id's of battle entities, this will ensure no double-registering
        self.entity_list = {}
    
        # Sprite group for drawing all entities
        self.spritegroup = pygame.sprite.OrderedUpdates()
        
        # Store the current round
        self.round = 0
        self.round_list = []
        self.round_timestamp = None
        
    def append_round (self, round_label, action_list):
        if self.verbose: print 'Added new round with',len(action_list),'actions.'
        self.round_list.append({'label': round_label, 'actions': action_list})
        
    def start_battle (self):
        if len(self.round_list) == 0:
            return
        
        # State of the battle
        self.battle_active = True
        
        # Current round
        self.round = 0
        
        # Start round
        self.next_round()
        
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
                    weapon = entities.LaserBlast(self.entity_list[action.source_reference].weapon, source_position, destination_position)
                    self.spritegroup.add(weapon)
                else:
                    print 'Warning Unknown weapon', self.entity_list[action.source_reference], self.entity_list[action.source_reference].weapon
            elif isinstance(action, actions.Death):
                self.entity_list[action.reference].death()
        # Incriment the round
        self.round += 1
        
    def log_message (self, message):
        print "Log message:",message
                
    def update (self):
        if not self.battle_active:
            return
        
        # Round completed flag
        complete = True
        
        #~ # Update all sprites - we manually do this so we can determin if all sprites are idle
        for sprite in self.spritegroup:
            # Tell the entity to update
            sprite.update()
            if not sprite.is_idle():
                complete = False
        
        # Redraw sprites
        rectlist = self.spritegroup.draw(self.display_surface)
        pygame.display.update(rectlist)
        self.spritegroup.clear(self.display_surface, self.background_surface)
        
        if complete:
            if self.round_timestamp == None:
                self.round_timestamp = pygame.time.get_ticks() + self.round_delay
            elif self.round_timestamp < pygame.time.get_ticks():
                self.round_timestamp = None
                self.next_round()
            
    def append_entity (self, side, reference, name='', model=None, weapon_label=None, weapon_points=[]):
        weapon = weapons.new_weapon(weapon_label)
        if not self.entity_list.has_key(reference):
            entity = entities.BasicEntity(side, reference, name, model, weapon, weapon_points)
            self.entity_list[reference] = entity
            self.spritegroup.add(entity)
