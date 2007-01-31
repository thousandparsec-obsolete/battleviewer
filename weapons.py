class BasicLaser:
    width = 1
    duration = 500
    pulse = 1
    color = (255,255,255)
    surface = None
    
    def fire (self, source, destination):
        pass
        
    def draw (self, draw_surface):
        pass
        
class Laser2 (BasicLaser):
    width = 1
    duration = 800
    pulse = 50
    color = (255, 255, 0)
    
class Laser5 (BasicLaser):
    width = 2
    duration = 900
    pulse = 20
    color = (255, 0, 0)
    
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
