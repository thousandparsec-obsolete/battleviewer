class BasicLaser:
    width = 0
    color = (255,255,255)
    surface = None
    
    def fire (self, source, destination):
        pass
        
    def draw (self, draw_surface):
        pass
        
class Laser2 (BasicLaser):
    width = 1
    color = (255, 255, 0)
    
class Laser5 (BasicLaser):
    width = 2
    color = (255, 0, 0)
    
def new_weapon (self, label=None):
    weapon = None
    if label:
        # Create the right kind of weapon, should probably be turned into a LUT somewhere
        if label == 'laser5':
            weapon = weapons.Laser5()
        elif label == 'laser2':
            weapon = weapons.Laser2()
        else:
            weapon = weapons.BasicLaser()
    return weapon