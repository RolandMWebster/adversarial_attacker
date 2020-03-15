import tcod as libtcod

from components.fighter import Fighter
from death_functions import kill_monster, kill_player
from render_functions import render_all, clear_all, RenderOrder
from entity import Entity, get_blocking_entities_at_location
from fov_functions import initialize_fov, recompute_fov
from map_objects.game_map import GameMap
from game_messages import Message, MessageLog
from game_states import GameStates
from input_handlers import handle_keys, handle_mouse
from components.inventory import Inventory



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
    max_items_per_room = 20

    colors = {
        'dark_wall': libtcod.Color(0, 0, 100),
        'dark_ground': libtcod.Color(50, 50, 150),
        'light_wall': libtcod.Color(130, 110, 50),
        'light_ground': libtcod.Color(200, 180, 50),

        'npc_dt': libtcod.Color(11, 102, 35)

    }

    # define our fighter component
    fighter_component = Fighter(hp = 30, defense = 2, power = 5)

    # define our inventory component
    inventory_component = Inventory(26)

    # spawn player
    player = Entity(0, 0, '@', libtcod.white, name = 'Player', blocks = True, render_order = RenderOrder.ACTOR, 
                    fighter = fighter_component, inventory = inventory_component)

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
    game_map.make_map(max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, 
                      max_monsters_per_room, max_items_per_room)
    
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
    previous_game_state = game_state
    
    # this is for targeting items:
    # the engine needs to remember which item we selected when we swap the game state to TARGETING
    # we can store the targeting_item so that the engine can recall it when actually using the item
    targeting_item = None


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
                   screen_width, screen_height, bar_width, panel_height, panel_y, mouse, colors, game_state)

        # do not recompute fov by default - only if the player moves
        fov_recompute = False

        # this line presents everything on the screen
        libtcod.console_flush()
        
        # clears previous characters from the screen. This stops us from creating
        # a snake on the screen while we move
        clear_all(con, entities)

        # use the handle_keys function that we created to translate our key press into an action
        action = handle_keys(key, game_state)

        # use the handle mouse function to  translate our mouse action into a game action
        mouse_action = handle_mouse(mouse)

        # grab our actions (if they exist)
        move = action.get('move')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')        
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')
        

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

        elif pickup and game_state == GameStates.PLAYERS_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break

            else:
                message_log.add_message(Message('There is nothing here to pick up.', libtcod.yellow))

        # show inventory
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(
                player.inventory.items):
            item = player.inventory.items[inventory_index]

            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))
        

        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(targeting_item, entities = entities, fov_map = fov_map,
                                                        target_x=target_x, target_y=target_y)

                player_turn_results.extend(item_use_results)
            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})


         # exit commands
        if exit:
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                return True

        # go fullscreen if that was the action taken by the user
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen()) 
        
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')

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


            if item_added:
                # remove item from map if we've picked it up
                entities.remove(item_added)

                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)

                game_state = GameStates.ENEMY_TURN

            if targeting:
                previous_game_state = GameStates.PLAYERS_TURN
                game_state = GameStates.TARGETING

                targeting_item = targeting

                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state

                message_log.add_message(Message('Targeting cancelled'))

        # let the enemies have their turn
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


