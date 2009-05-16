class Action:
    def execute (self):
        pass
    
class Log (Action):
    def __init__ (self, message):
        self.message = message

class Fire (Action):
    def __init__ (self, source_reference, destination_reference):
        self.source_reference = source_reference
        self.destination_reference = destination_reference
        
class Damage (Action):
    def __init__ (self, reference, amount):
        self.reference = reference
        self.amount = amount
        
class Death (Action):
    def __init__ (self, reference):
        self.reference = reference
