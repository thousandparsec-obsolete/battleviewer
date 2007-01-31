import pygame, battleview, actions
    
def main ():
    # Initialize pygame
    pygame.display.init()
    
    # Framerate Clock
    clock = pygame.time.Clock()
    
    # Desired delay between frame redraws (25 fps target framerate)
    frame_delay = 1000/25
    
    # Create the display
    display_size = (340,540)
    display_depth = 24
    display_surface = pygame.display.set_mode(display_size, 0, display_depth)
    
    # Create our battle view instance
    battle_view = battleview.BattleView(display_surface)
    
    # Combat Entities
    
    # Mithro
    battle_view.append_entity('mithro', 'battleship-54-1', "Mithro's Super Fleet, Battleship 1",  'graphics/battleship/model.png', 'laser5')
    battle_view.append_entity('mithro', 'battleship-54-2', "Mithro's Super Fleet, Battleship 2",  'graphics/battleship/model.png', 'laser5')
    battle_view.append_entity('mithro', 'planet-23', "Mithro's Colony on Omega 1",  'graphics/planet/model.png', 'laser5')
    
    # Lee
    battle_view.append_entity('lee', 'scout-59-1', "Lee's Super Fleet, Scout 1",  'graphics/scout/model.png')
    battle_view.append_entity('lee', 'battleship-59-2', "Mithro's Super Fleet, Battleship 2",  'graphics/battleship/model.png', 'laser5')
    battle_view.append_entity('lee', 'frigate-59-3', "Lee's Super Fleet, Frigate 1",  'graphics/frigate/model.png', 'laser2')
    
    # Combat Script
    
    # Round 1
    round = []
    round.append(actions.Log("Battle between Lee's Super Fleet and Mithro's killer fleet started."))
    round.append(actions.Move('battleship-54-1', (0,0)))
    round.append(actions.Move('battleship-54-2', (100,0)))
    round.append(actions.Move('planet-23', (200,0)))
    round.append(actions.Move('scout-59-1', (0,400)))
    round.append(actions.Move('battleship-59-2', (100,400)))
    round.append(actions.Move('frigate-59-3', (200, 400)))
    
    # Add the round to the battle view
    battle_view.append_round(round)
    
    # Round 2
    round = []
    round.append(actions.Log("Lee's fleet chooses rock."))
    round.append(actions.Log("Mithro's fleet chooses paper."))
    round.append(actions.Log("Lee's fleet wins."))
    round.append(actions.Fire('frigate-59-3', (0,0), 'battleship-54-1', (0,0)))
    round.append(actions.Fire('battleship-59-2', (0,0), 'battleship-54-2', (0,0)))
    round.append(actions.Damage('battleship-59-1', 2))
    round.append(actions.Damage('battleship-54-2', 3))
    
    # Add the round to the battle view
    battle_view.append_round(round)
    
    # Start the battle
    battle_view.start_battle()
    
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
        battle_view.update()
        
        # Sleep the main loop for the desired time
        if running: clock.tick(frame_delay)
        
if __name__ == '__main__':
    main()
