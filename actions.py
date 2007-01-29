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