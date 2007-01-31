# Lets you use barewords to refer to states

class State:
    label = None
    def __init__ (self, label):
        self.label = label
    def __repr__ (self):
        return '<State %s label="%s">' % (id(self), self.label)
        
class States:
    counter = 0
    def __init__ (self, *state_list):
        for state in state_list:
            self.__dict__[state] = State(state)
            States.counter += 1
