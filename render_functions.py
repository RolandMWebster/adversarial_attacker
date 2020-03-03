# Functions to render various objects.

import tcod as libtcod


def render_all(con, entities, game_map, screen_width, screen_height, colors):
    
    # Draw all the tiles in the game map.
    for y in range(game_map.height):
        for x in range(game_map.width):

            # Determine whether the current tile is a wall or not
            wall = game_map.tiles[x][y].block_sight

            # Color our tile appropriately
            if wall:
                libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
            else:
                libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)
    
    # Draw all entities in the list
    for entity in entities:
        # Use our draw_entity function.
        draw_entity(con, entity)

     # This part actually draws our entity on the console.
    libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    # Clears all entities
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity):

    # Provides the font color for our foreground, which is the actual symbol that we're drawing.
    # The first arguement is the console that we're drawing to, second is our entities color.
    libtcod.console_set_default_foreground(con, entity.color)

    # The first argument is the console we're printing to.
    # The second and third arguments are x and y coordinates for where to draw.
    # The third argument is what to draw.
    # The fourth argument sets the background to none.
    libtcod.console_put_char(con, entity.x, entity.y, entity.char, libtcod.BKGND_NONE)


def clear_entity(con, entity):
    # erase the character that represents this object
    libtcod.console_put_char(con, entity.x, entity.y, ' ', libtcod.BKGND_NONE)