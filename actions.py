class Action:
    def execute (self):
        pass
    
class Log (Action):
    message = ''
    def __init__ (self, message):
        self.message = message
        
class Move (Action):
    id = None
    position = None
    def __init__(self, id, position):
        self.id = id
        self.position = position

class Fire (Action):
    source_id = None
    source_position = None
    destination_id = None
    destination_position = None
    
    def __init__ (self, source_id, source_position, destination_id, destination_position):
        self.source_id = source_id
        self.source_position = source_position
        self.destination_id = destination_id
        self.destination_position = destination_position
        
class Damage (Action):
    id = None
    amount = 0
    
    def __init__ (self, id, amount):
        self.id = id
        self.amount = amount
