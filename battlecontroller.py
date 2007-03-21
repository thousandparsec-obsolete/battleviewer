from ocempgui.object import BaseObject
import constants, actions, weapons, entities

class BattleController (BaseObject):
    
    verbose = True
    
    def __init__ (self):
        BaseObject.__init__(self)
        
        self._signals[constants.EVENT_BATTLE_START] = []
        self._signals[constants.EVENT_VIEW_READY] = []
        
        self.entity_list = {}
        
        # Store the current round
        self.round = 0
        self.round_list = []
        self.round_timestamp = None
        
    def on_battle_start (self):
        # Current round
        self.round = 0
        
    def on_view_ready (self):
        print 'view ready'
        self.next_round()
        
    def notify (self, event):
        if event.signal == constants.EVENT_BATTLE_START:
            self.on_battle_start()
        elif event.signal == constants.EVENT_VIEW_READY:
            self.on_view_ready()

    def append_round (self, round_label, action_list):
        if self.verbose: print 'Added new round with',len(action_list),'actions.'
        self.round_list.append({'label': round_label, 'actions': action_list})

    def append_entity (self, side, reference, name='', model=None, weapon_label=None, weapon_points=[]):
        if not self.entity_list.has_key(reference):
            weapon = weapons.make_weapon(weapon_label)
            entity = entities.BasicEntity(self.manager, side, reference, name, model, weapon, weapon_points)
            self.entity_list[reference] = entity
            self.emit(constants.EVENT_ENTITY_NEW, entity)
        else:
            if self.verbose: print 'Warning: duplicate entity'
    
    def next_round (self):
        if len(self.round_list) == 0:
            return
            
        if self.round == len(self.round_list):
            # Finished all rounds
            if self.verbose: print 'Battle ended.'
            return
        
        # process actions
        if self.verbose: print 'Starting round', self.round_list[self.round]['label']
        for action in self.round_list[self.round]['actions']:
            if isinstance(action, actions.Log):
                self.emit(constants.EVENT_MESSAGE, (action.message))
            elif isinstance(action, actions.Fire):
                self.emit(constants.EVENT_ENTITY_FIRE, (action.source_reference, self.entity_list[action.destination_reference]))
            elif isinstance(action, actions.Damage):
                self.emit(constants.EVENT_ENTITY_DAMAGE, (action.reference, action.amount))
            elif isinstance(action, actions.Death):
                self.emit(constants.EVENT_ENTITY_DEATH, (action.reference))
        
        # Signal the round has begun
        self.emit(constants.EVENT_ROUND_START, 0)
        
        # Incriment the round
        self.round += 1