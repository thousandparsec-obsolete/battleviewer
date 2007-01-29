import pygame, actions, weapons, entitys

class BattleView:
    # Reference to the pygame display surface
    display_surface = None
    background_surface = None
    entity_list = None
    round = 0
    round_list = None
    battle_active = False
    entity_spritegroup = None
    
    def __init__ (self, display_size, display_depth):
        # Initialize the display
        self.display_surface = pygame.display.set_mode(display_size, 0, display_depth)
    
        # Create a background surface
        background_color = (0,0,0)
        self.background_surface = pygame.surface.Surface(display_size)
        self.background_surface.fill(background_color)
        
        # Blit the background surface to the display surface
        self.display_surface.blit(self.background_surface, (0,0))
    
        # Update the whole display
        pygame.display.flip()
        
        # List to contain battle entities
        self.entity_list = {}
    
        # Sprite group for drawing all entities
        self.entity_spritegroup = pygame.sprite.RenderUpdates()
        
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
            if isinstance(action, actions.Move):
                if self.entity_list.has_key(action.id):
                    self.entity_list[action.id].move(action.position)
                else:
                    print 'Entity ID',action.id,'not in entity list.'
        
        # Incriment the round
        self.round += 1
        
    def log_message (self, message):
        print "Log message:",message
                
    def update (self):
        if not self.battle_active:
            return
        
        # Round completed flag
        complete = True
        
        #~ # Update all entities
        for entity in self.entity_list.itervalues():
            # Tell the entity to update
            entity.update()
            if not entity.is_idle():
                complete = False
        
        # Redraw sprites
        rectlist = self.entity_spritegroup.draw(self.display_surface)
        pygame.display.update(rectlist)
        self.entity_spritegroup.clear(self.display_surface, self.background_surface)
        
        if complete:
            print "round complete"
            self.next_round()
            
    def append_entity (self, side, id, name='', model=None, weapon_label=None):
        weapon = weapons.new_weapon(weapon_label)
        if not self.entity_list.has_key(id):
            entity = entitys.BasicEntity(side, id, name, model, weapon)
            self.entity_list[id] = entity
            self.entity_spritegroup.add(entity)