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
        
    def append_round (self, action_list):
        print 'Added new round with',len(action_list),'actions.'
        self.round_list.append(action_list)
        
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
            print 'Battle ended.'
            return
        
        # process actions
        for action in self.round_list[self.round]:
            # I know isinstance is evil, but it's so useful
            if isinstance(action, actions.Log):
                self.log_message(action.message)
            elif isinstance(action, actions.Move):
                if self.entity_list.has_key(action.id):
                    self.entity_list[action.id].move(action.position)
                else:
                    print 'Entity ID',action.id,'not in entity list.'
            elif isinstance(action, actions.Fire):
                source_position = self.entity_list[action.source_id].get_position()
                destination_position = self.entity_list[action.destination_id].get_position()
                if isinstance(self.entity_list[action.source_id].weapon, weapons.BasicLaser):
                    # laser weapon
                    weapon = entities.LaserBlast(self.entity_list[action.source_id].weapon, source_position, destination_position)
                    self.spritegroup.add(weapon)
                else:
                    print 'Warning Unknown weapon', self.entity_list[action.source_id], self.entity_list[action.source_id].weapon
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
            self.next_round()
            
    def append_entity (self, side, id, name='', model=None, weapon_label=None):
        weapon = weapons.new_weapon(weapon_label)
        if not self.entity_list.has_key(id):
            entity = entities.BasicEntity(side, id, name, model, weapon)
            self.entity_list[id] = entity
            self.spritegroup.add(entity)
