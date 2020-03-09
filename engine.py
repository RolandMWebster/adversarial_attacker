import tcod as libtcod

from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from render_functions import render_all, clear_all, RenderOrder
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from map_objects.game_map import GameMap
from game_messages import MessageLog
from game_states import GameStates
from input_handlers import handle_keys


def main():
    # Setting the screen size
    screen_width = 80
    screen_height = 50

    bar_width = 20
    panel_height = 7
    panel_y = screen_height - panel_height

    message_x = bar_width + 2
    message_width = screen_width - bar_width - 2
    message_height = panel_height - 1

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    fov_algorithm = 0
    fov_light_walls = True
    fov_radius = 10

    max_monsters_per_room = 3

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50),

        'npc_dt': libtcod.Color(11, 102, 35)

    }

    # define our fighter component
    fighter_component = Fighter(hp = 30, defense = 2, power = 5)

    # spawn player
    player = Entity(0, 0, '@', libtcod.white, name = 'Player', blocks = True, render_order = RenderOrder.ACTOR, fighter = fighter_component)

    # initialize entities with the player in it
    entities = [player]

    # telling libtcod which font to use. We read the font details from the arial10x10.png file that we saved down.
    # the other two parts are telling libtcod which type of file we're reading.
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # this line actually creates the screen, using the screen heigh and width that we specified.
    # the boolean at the end tells it whether to go full screen or not.
    libtcod.console_init_root(screen_width, screen_height, 'Adversarial Attacker', False)

    # define console
    con = libtcod.console_new(screen_width, screen_height)

    # define panel
    panel = libtcod.console_new(screen_width, panel_height)

    # generate a game map
    game_map = GameMap(map_width, map_height)
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_monsters_per_room)
    
    # boolean to determine whether the field of view needs to be computed
    # it is True by default because we need to compute it when the game starts
    fov_recompute = True

    fov_map = initialize_fov(game_map)

    # start our message log
    message_log = MessageLog(message_x, message_width, message_height)

    # variables to hold our keyboard and mouse inputs
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # variable to store the game state
    game_state = GameStates.PLAYERS_TURN

    # this begins what's called our 'game loop'. This won't end until we close the game
    while not libtcod.console_is_window_closed():

        # this line captures new events (inputs from the user)
        # this updates the key variable with the user input but doesn't actually do anything with it yet
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS | libtcod.EVENT_MOUSE, key, mouse)

        # recompute field of view if required
        if fov_recompute:
            recompute_fov(fov_map, player.x, player.y, fov_radius, fov_light_walls, fov_algorithm)

        # render everything
        render_all(con, panel, entities, player, game_map, fov_map, fov_recompute, message_log,
                   screen_width, screen_height, bar_width, panel_height, panel_y, mouse, colors)

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

        # initialize the results of the upcoming turn
        player_turn_results = []

        # carry out our movement action if it exists
        if move and game_state == GameStates.PLAYERS_TURN:
            # set dx and dy values to our move coordinates
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            # check whether the move location is blocked
            if not game_map.is_blocked(destination_x, destination_y):
                # check whethere there is a blocking entity in our destination
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                # if so, kick it
                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)

                else:

                    # update player (x,y) position using (dx,dy)
                    player.move(dx, dy)

                    # we need to update the fov since our player has moved
                    fov_recompute = True
                
                game_state = GameStates.ENEMY_TURN

         # exit the game if that was the action taken by the user
        if exit:
            return True

        # go fullscreen if that was the action taken by the user
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen()) 
        
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')

            if message:
                message_log.add_message(message)

            # handle something dying
            if dead_entity:
                
                # if our player died then run the kill_player function
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                # else we run the kill_monster function (since it must be a monster that is dead)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

          


        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            
                            if dead_entity == player:
                                message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYERS_TURN


if __name__ == '__main__':
    main()


