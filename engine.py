import tcod as libtcod

from input_handlers import handle_keys

def main():
    # Setting the screen size
    screen_width = 80
    screen_height = 50

    # Variables to keep track of player position
    player_x = int(screen_width/2)
    player_y = int(screen_height/2)

    # Telling libtcod which font to use. We read the font details from the arial10x10.png file that we saved down.
    # The other two parts are telling libtcod which type of file we're reading.
    libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    # This line actually creates the screen, using the screen heigh and width that we specified.
    # The boolean at the end tells it whether to go full screen or not.
    libtcod.console_init_root(screen_width, screen_height, 'Adversarial Attacker', False)

    # Define console
    con = libtcod.console_new(screen_width, screen_height)

    # Variables to hold our keyboard and mouse inputs.
    key = libtcod.Key()
    mouse = libtcod.Mouse()

    # This begins what's called our 'game loop'. This won't end until we close the game.
    while not libtcod.console_is_window_closed():

        # This line captures new events (inputs from the user)
        # This updates the key variable with the user input but doesn't actually do anything with it yet.
        libtcod.sys_check_for_event(libtcod.EVENT_KEY_PRESS, key, mouse)

        # Provides the font color for our foreground, which is our '@' symbol.
        # The first arguement is the console we're drawing to.
        libtcod.console_set_default_foreground(con, libtcod.white)

        # The first argument is the console we're printing to again.
        # The second and third arguments are x and y coordinates for where to draw.
        # The third argument is what to draw.
        # The fourth argument sets the background to none.
        libtcod.console_put_char(con, player_x, player_y, "@", libtcod.BKGND_NONE)
        
        # This part actually draws our symbol.
        libtcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)

        # This line presents everything on the screen.
        libtcod.console_flush()

        # Removes the trailing '@' symbol when we move (so that we don't create a snake).
        libtcod.console_put_char(con, player_x, player_y, ' ', libtcod.BKGND_NONE)

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
            # Update player (x,y) position using (dx,dy).
            player_x += dx
            player_y += dy

        # Exit the game if that was the action taken by the user.
        if exit:
            return True

        # Go fullscreen if that was the action taken by the user.
        if fullscreen:
            libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen()) 
        
        

if __name__ == '__main__':
    main()


