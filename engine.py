import tcod as libtcod

from render_functions import render_all, clear_all
from entity import Entity
from map_objects.game_map import GameMap
from input_handlers import handle_keys

def main():
    # Setting the screen size
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    colors = {
        'dark_wall': libtcod.Color(169, 169, 169),
        'dark_ground': libtcod.Color(107, 75, 65),
        'npc_dt': libtcod.Color(11, 102, 35)
    }


    # Spawn entities
    player = Entity(int(screen_width / 2), int(screen_height / 2 ), "@", libtcod.white)
    npc_dt = Entity(int(screen_width / 2 - 5), int(screen_height / 2 ), "@", colors.get('npc_dt'))

    # Store entities
    entities = [
        player, 
        npc_dt
        ]

    # Telling libtcod which font to use. We read the font details from the arial10x10.png file that we saved down.
    # The other two parts are telling libtcod which type of file we're reading.
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # This line actually creates the screen, using the screen heigh and width that we specified.
    # The boolean at the end tells it whether to go full screen or not.
    libtcod.console_init_root(screen_width, screen_height, 'Adversarial Attacker', False)

    # Define console
    con = libtcod.console_new(screen_width, screen_height)

    # Generate a game map
    game_map = GameMap(map_width, map_height)

    # Variables to hold our keyboard and mouse inputs.
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # This begins what's called our 'game loop'. This won't end until we close the game.
    while not libtcod.console_is_window_closed():

        # This line captures new events (inputs from the user)
        # This updates the key variable with the user input but doesn't actually do anything with it yet.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # Render our entities
        render_all(con, entities, game_map, screen_width, screen_height, colors)

        # This line presents everything on the screen.
        libtcod.console_flush()
        
        # Clears previous characters from the screen. This stops us from creating
        # a snake on the screen while we move.
        clear_all(con, entities)

        # Use the handle_keys function that we created to translate our key press into an action.
        action = handle_keys(key)

        # Grab our actions (if they exist)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        # Carry out our movement action if it exists.
        if move:
            # Set dx and dy values to our move coordinates.
            dx, dy = move

            # Check whether the move location is blocked.
            if not game_map.is_blocked(player.x + dx, player.y + dy):

                # Update player (x,y) position using (dx,dy).
                player.move(dx, dy)

        # Exit the game if that was the action taken by the user.
        if exit:
            return True

        # Go fullscreen if that was the action taken by the user.
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen()) 
        
        

if __name__ == '__main__':
    main()


