# Functions to render various objects.

import tcod as libtcod

from enum import Enum

class RenderOrder(Enum):
    CORPSE = 1
    ITEM = 2
    ACTOR = 3

def render_all(con, entities, player, game_map, fov_map, fov_recompute, screen_width, screen_height, colors):
    
    if fov_recompute:

        for y in range(game_map.height):
            for x in range(game_map.width):
                
                # determine whether the current tile is visible (in fov) or not
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                
                # determine whether the current tile is a wall or not
                wall = game_map.tiles[x][y].block_sight

                # color the tile appropriately
                if visible:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, colors.get('light_wall'), libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('light_ground'), libtcod.BKGND_SET)

                    game_map.tiles[x][y].explored = True


                elif game_map.tiles[x][y].explored:
                    if wall:
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_wall'), libtcod.BKGND_SET)
                    else:
                        libtcod.console_set_char_background(con, x, y, colors.get('dark_ground'), libtcod.BKGND_SET)

        # reorder our entities into rendering order
        entities_in_render_order = sorted(entities, key = lambda x: x.render_order.value)
        
        # draw all entities in the list
        for entity in entities_in_render_order:
            # use our draw_entity function.
            draw_entity(con, entity, fov_map)

        libtcod.console_set_default_foreground(con, libtcod.white)
        libtcod.console_print_ex(con, 1, screen_height - 2, libtcod.BKGND_NONE, libtcod.LEFT,
                                'HP: {0:02}/{1:02}'.format(player.fighter.hp, player.fighter.max_hp))

        # this part actually draws our entity on the console.
        libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


def clear_all(con, entities):
    # clears all entities
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map):

    # check if entity is in fov:
    if libtcod.map_is_in_fov(fov_map, entity.x, entity.y):
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