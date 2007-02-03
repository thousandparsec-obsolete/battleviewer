class Action:
    def execute (self):
        pass
    
class Log (Action):
    message = ''
    def __init__ (self, message):
        self.message = message
        
class Move (Action):
    reference = None
    position = None
    def __init__ (self, reference, position):
        self.reference = reference
        self.position = position

class Fire (Action):
    source_reference = None
    destination_reference = None
    
    def __init__ (self, source_reference, destination_reference):
        self.source_reference = source_reference
        self.destination_reference = destination_reference
        
class Damage (Action):
    reference = None
    amount = 0
    
    def __init__ (self, reference, amount):
        self.reference = reference
        self.amount = amount
        
class Death (Action):
    reference = None
    
    def __init__ (self, reference):
        self.reference = reference
