class BasicLaser:
    width = 3
    duration = 500
    pulse = 1
    color = (0,0,255)
    surface = None
    
    def fire (self, source, destination):
        pass
        
    def draw (self, draw_surface):
        pass
        
class Laser2 (BasicLaser):
    width = 3
    duration = 800
    pulse = 1
    color = (128,0,255)
    
class Laser5 (BasicLaser):
    width = 5
    duration = 900
    pulse = 1
    color = (255,128,0)
    
def new_weapon (label=None):
    weapon = None
    if label:
        # Create the right kind of weapon, should probably be turned into a LUT somewhere
        if label == 'laser5':
            weapon = Laser5()
        elif label == 'laser2':
            weapon = Laser2()
        else:
            weapon = BasicLaser()
    return weapon
