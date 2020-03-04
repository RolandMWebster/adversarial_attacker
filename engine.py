import tcod as libtcod

from render_functions import render_all, clear_all
from entity import Entity
from fov_functions import initialize_fov, recompute_fov
from map_objects.game_map import GameMap
from input_handlers import handle_keys


def main():
    # Setting the screen size
    screen_width = 80
    screen_height = 50
    map_width = 80
    map_height = 45

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50),

        'npc_dt': libtcod.Color(11, 102, 35)

    }


    # Spawn entities
    player = Entity(int(screen_width / 2), int(screen_height / 2 ), "@", libtcod.white)
    npc_dt = Entity(int(screen_width / 2 - 5), int(screen_height / 2 ), "@", colors.get('npc_dt'))

    # store entities
    entities = [
        player, 
        npc_dt
        ]

    # telling libtcod which font to use. We read the font details from the arial10x10.png file that we saved down.
    # the other two parts are telling libtcod which type of file we're reading.
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # this line actually creates the screen, using the screen heigh and width that we specified.
    # the boolean at the end tells it whether to go full screen or not.
    libtcod.console_init_root(screen_width, screen_height, 'Adversarial Attacker', False)

    # define console
    con = libtcod.console_new(screen_width, screen_height)

    # generate a game map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player)
    
    # boolean to determine whether the field of view needs to be computed
    # it is True by default because we need to compute it when the game starts
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    # variables to hold our keyboard and mouse inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # this begins what's called our 'game loop'. This won't end until we close the game
    while not libtcod.console_is_window_closed():

        # this line captures new events (inputs from the user)
        # this updates the key variable with the user input but doesn't actually do anything with it yet
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # recompute field of view if required
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        # render our entities
        render_all(con, entities, game_map, fov_map, fov_recompute, screen_width, screen_height, colors)

        # do not recompute fov by default - only if the player moves
        fov_recompute = False

        # this line presents everything on the screen
        libtcod.console_flush()
        
        # clears previous characters from the screen. This stops us from creating
        # a snake on the screen while we move
        clear_all(con, entities)

        # use the handle_keys function that we created to translate our key press into an action
        action = handle_keys(key)

        # grab our actions (if they exist)
        move = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        # carry out our movement action if it exists
        if move:
            # set dx and dy values to our move coordinates
            dx, dy = move

            # check whether the move location is blocked
            if not game_map.is_blocked(player.x + dx, player.y + dy):

                # update player (x,y) position using (dx,dy)
                player.move(dx, dy)

                # we need to update the fov since our player has moved
                fov_recompute = True

        # exit the game if that was the action taken by the user
        if exit:
            return True

        # go fullscreen if that was the action taken by the user
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen()) 
        
        

if __name__ == '__main__':
    main()


