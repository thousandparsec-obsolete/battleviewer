import sys
sys.path.append('..')
import pygame, entities, random

class View:
    def __init__ (self, display_surface, background_surface):
        # Initialize the display
        self.display_surface = display_surface
        
        self.background_surface = background_surface
        
        # Blit the background surface to the display surface
        self.display_surface.blit(self.background_surface, (0,0))

        # Update the whole display
        pygame.display.flip()
        
        # List to contain id's of battle entities, this will ensure no double-registering
        self.entity_list = {}
    
        # Sprite group for drawing all entities
        self.spritegroup = pygame.sprite.OrderedUpdates()
                
    def update (self):
        self.spritegroup.update()
        
        # Redraw sprites
        rectlist = self.spritegroup.draw(self.display_surface)
        pygame.display.update(rectlist)
        self.spritegroup.clear(self.display_surface, self.background_surface)

    def append_entity (self, entity):
        self.spritegroup.add(entity)
            
def main ():
    # Initialize pygame
    pygame.display.init()
    
    # Initialize fonts
    pygame.font.init()
    
    # Framerate Clock
    clock = pygame.time.Clock()
    
    # Desired delay between frame redraws (25 fps target framerate)
    frame_delay = 1000/25
    
    # Load background surface
    background_surface = pygame.image.load('./background.png')
    
    # Create the display
    display_padding = 12
    display_size = (display_padding*2 + 128*3, display_padding*2 + 400+128)
    display_depth = 32
    display_surface = pygame.display.set_mode((background_surface.get_width()/2, background_surface.get_height()), 0, display_depth)
    
    background_surface = background_surface.convert()
    
    # view
    view = View(display_surface, background_surface)
    
    # Damage animation
    margin = 75
    xmin = margin
    xmax = (background_surface.get_width()/2) - margin
    ymin = background_surface.get_height() - 200
    ymax = background_surface.get_height() - margin
    for n in range(50):
        damage_amount = random.randrange(-11,11)
        position = (random.randrange(xmin,xmax), random.randrange(ymin,ymax))
        speed = random.randrange(5000,7000)
        wait = random.randrange(500,2000)
        damage_animation = entities.DamageAnimation(damage_amount, position, speed, wait, '../fonts/')
        view.append_entity(damage_animation)
    
    # Event loop
    running = True
    while running:
        for event in pygame.event.get():
            # Quit event, stop event loop
            if event.type == pygame.QUIT:
                running = False
            # Detect if a key was pressed
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Propigate the update event to our battle view
        view.update()
        
        # Sleep the main loop for the desired time
        if running: clock.tick(frame_delay)
        
if __name__ == '__main__':
    main()