from ocempgui.object import BaseObject
from ocempgui.events import EventManager, INotifyable

# Events

EVENT_ENTITY_NEW = intern ("new entity")
EVENT_ENTITY_MOVE = intern ("entity move")

# Entity class. Element in battle scene

class Entity (BaseObject):
    def __init__ (self, name):
        BaseObject.__init__(self)
        self._signals[EVENT_ENTITY_MOVE] = []
        self.name = name
        
    def move (self, position):
        print 'entity',self.name,'moving to',position
        
    def notify (self, event):
        if event.signal == EVENT_ENTITY_MOVE:
            if event.data[0] == self.name:
                self.move(event.data[1])

# BattleView class. Responsible for drawing entities

class BattleView (BaseObject):
    def __init__ (self):
        BaseObject.__init__(self)
        self._signals[EVENT_ENTITY_NEW] = []
        self.entity_list = []
        
    def append_entity (self, entity):
        self.entity_list.append(entity)
        entity.manager = self.manager
        
    def notify (self, event):
        if event.signal == EVENT_ENTITY_NEW:
            name, position = event.data
            self.append_entity(Entity(name))
            self.emit(EVENT_ENTITY_MOVE, (name, position))
            
# BattleController class.  Responsible for distributing battle events

class BattleController (BaseObject):
    def __init__ (self):
        BaseObject.__init__(self)
    
    def start (self):
        entity_list = ['Sam', 'Max', 'Joe']
        for entity_name in entity_list:
            self.emit(EVENT_ENTITY_NEW, (entity_name, (0, 0)))

# Main

if __name__ == '__main__':
    event_manager = EventManager()
    
    controller = BattleController()
    controller.manager = event_manager
    
    view = BattleView()
    view.manager = event_manager
    
    # start the ball rolling
    controller.start()