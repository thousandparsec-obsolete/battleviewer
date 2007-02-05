import pygame, battleview, actions, battleparser

def main ():
    # Initialize pygame
    pygame.display.init()
    
    # Framerate Clock
    clock = pygame.time.Clock()
    
    # Desired delay between frame redraws (25 fps target framerate)
    frame_delay = 1000/25
    
    # Create the display
    display_padding = 12
    display_size = (display_padding*2 + 128*3, display_padding*2 + 400+128)
    display_depth = 24
    display_surface = pygame.display.set_mode(display_size, 0, display_depth)
    
    # Create our battle view instance
    battle_view = battleview.BattleView(display_surface)
    
    battle_parser = battleparser.Parser.CreateParser()
    battle_parser.ParseFile(file("example1.xml", "r"))

    battle = battle_parser.objects
    
    # Combat entities
    for side in battle.sides:
        for entity in battle.sides[side].itervalues():
            weapon_points = None
            if entity.weaponpoints:
                weapon_points = [(n[0], n[1]) for n in entity.weaponpoints[0]]
            battle_view.append_entity(side, entity.id, entity.name, entity.model, entity.weapontype, weapon_points)

    # Combat Script
    for round in battle.rounds:
        current_round = []
        for action in round.actions:
            # determin what kind of action it is
            if isinstance(action, battleparser.Parser.Log):
                current_round.append(actions.Log(action.data))
            elif isinstance(action, battleparser.Parser.Move):
                # adding the padding here to the position isn't the nicest idea.  all sprites should probably be rewritten to support nesting like UI widgets.
                current_round.append(actions.Move(action.reference, (action.position[0] + display_padding, action.position[1] + display_padding)))
            elif isinstance(action, battleparser.Parser.Fire):
                current_round.append(actions.Fire(action.source, action.destination))
            elif isinstance(action, battleparser.Parser.Damage):
                current_round.append(actions.Damage(action.reference, action.amount))
            elif isinstance(action, battleparser.Parser.Death):
                current_round.append(actions.Death(action.reference))
            else:
                print 'Unknown action', action
        battle_view.append_round(round.number, current_round)
    
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
