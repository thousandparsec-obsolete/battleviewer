#!/usr/bin/env python

import sys, pygame, battleview, battlecontroller, battleparser, xml_validator

import actions, constants

from ocempgui.object import BaseObject
from ocempgui.events import EventManager

battle_file = "./example1.xml"
    
def main ():
    # Initialize pygame
    pygame.display.init()
    pygame.font.init()
    
    # Framerate Clock
    clock = pygame.time.Clock()
    
    pygame.display.set_caption('Battle Viewer')
    
    # Desired delay between frame redraws (25 fps target framerate)
    frame_rate = 24
    
    # Create the display
    display_padding = 12
    # Values are hacked for specific XML, needs to be made generic in future
    display_size = (display_padding*2 + 128*4, display_padding*3 + 400+128)
    display_depth = 24
    display_surface = pygame.display.set_mode(display_size, 0, display_depth)
    
    # Event manager
    event_manager = EventManager()
    
    # Create the battle controller instance.  This object is responsible for directing the battle
    battle_controller = battlecontroller.BattleController()
    battle_controller.manager = event_manager
    
    # Create the battle view instance.  This object is responsible for drawing the battle
    battle_view = battleview.BattleView(display_surface)
    battle_view.manager = event_manager
    
    # Validate and Parse the battle XML
    try:
        xml_validator.validate_dtd(battle_file)
    except xml_validator.ValidationError, e:
        print battle_file, "Failed Validation:", repr(e)
        sys.exit(1)
    
    battle_parser = battleparser.Parser.CreateParser()
    battle_parser.ParseFile(file(battle_file, "r"))

    battle = battle_parser.objects
    
    # Combat entities
    for side in battle.sides:
        for entity in battle.sides[side].itervalues():
            weapon_points = None
            if entity.weaponpoints:
                weapon_points = [(n[0], n[1]) for n in entity.weaponpoints[0]]
            battle_controller.append_entity(side, entity.id, entity.name, entity.model,
                                            entity.weapontype, weapon_points)

    # Combat Script
    for round in battle.rounds:
        current_round = []
        for action in round.actions:
            # determin what kind of action it is
            if isinstance(action, battleparser.Parser.Log):
                current_round.append(actions.Log(action.data))
            elif isinstance(action, battleparser.Parser.Fire):
                current_round.append(actions.Fire(action.source, action.destination))
            elif isinstance(action, battleparser.Parser.Damage):
                current_round.append(actions.Damage(action.reference, action.amount))
            elif isinstance(action, battleparser.Parser.Death):
                current_round.append(actions.Death(action.reference))
            else:
                print 'Unknown action', action
        battle_controller.append_round(round.number, current_round)
    
    # Start the battle.  Event gets propigated in order of addition to event manager (controller then view).
    event_manager.emit(constants.EVENT_BATTLE_START, 0)
    
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
            elif event.type == pygame.VIDEOEXPOSE:
                # Force a redraw if the application comes to the foreground
                pygame.display.flip()
            
        # Call update on the battle view.  Could use an event here,
        # but it seems like unnessasary MVC purist overkill.
        battle_view.update()
        
        # Sleep the main loop for the desired time
        if running: clock.tick(frame_rate)
        
if __name__ == '__main__':
    main()
