import tcod as libtcod


def handle_keys(key):
    '''
    Handles transforming key presses into actions with our game. This works by returning a 
    dictionary that is dependant on the key pressed by the user.
    '''

    key_char = chr(key.c)

    # Moving
    if key.vk == libtcod.KEY_UP or key_char == 'k':
        return {'move': (0, -1)}
    elif key.vk == libtcod.KEY_DOWN or key_char == 'j':
        return {'move': (0, 1)}
    elif key.vk == libtcod.KEY_LEFT or key_char == 'h':
        return {'move': (-1, 0)}
    elif key.vk == libtcod.KEY_RIGHT or key_char == 'l':
        return {'move': (1, 0)}
    elif key_char == 'y':
        return {'move': (-1, -1)}
    elif key_char == 'u':
        return {'move': (1, -1)}
    elif key_char == 'b':
        return {'move': (-1, 1)}    
    elif key_char == 'n':
        return {'move': (1, 1)}


    # Fullscreening the game
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        # Alt+Enter: toggle full screen
        return {'fullscreen': True}

    # Exiting the game
    elif key.vk == libtcod.KEY_ESCAPE:
        # Exit the game
        return {'exit': True}

    # No key was pressed - this is here becasue our engine will be expecting a dictionary, so we must
    # return something, even if nothing happens.
    return {}