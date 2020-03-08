import tcod as libtcod
from random import randint

from entity import Entity
from map_objects.rectangle import Rect
from map_objects.tile import Tile


class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        # generate a 2d arary of blocked tiles that fill our map. We'll 
        # then 'dig' a path to create the map
        tiles = [[Tile(True) for y in range(self.height)] for x in range(self.width)]

        return tiles

    def is_blocked(self, x, y):
        # returns true if tile is blocked, returns false otherwise
        if self.tiles[x][y].blocked:
            return True
        
        return False

    def make_map(self, max_rooms, room_min_size, room_max_size, map_width, map_height, player, entities, max_mosters_per_room):

        # initialize rooms
        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position without going out of the boundaries of the map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # the "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            for other_room in rooms:
                if new_room.intersect(other_room):
                    break
            else:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, this is where the player starts
                    player.x = new_x
                    player.y = new_y
                else:
                    # all rooms after the first follow this path
                    # connect to the previous room with a tunnel
                    # start by getting center coordinates of previous room
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # flip a coin:
                    if randint(0,1) == 1:
                        # first dig tunnel horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x) 
                    else:
                        # first dig tunnel vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities, max_mosters_per_room)

                # finally, append the new room to the list and increment room count
                rooms.append(new_room)
                num_rooms += 1


                    
    def create_room(self, room):
        # go through the titles in the rectangle and make them passable
        # the + 1 in our loops avoids rooms becoming connected when made
        # right next to eachother
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False
    
    def create_h_tunnel(self, x1, x2, y):
        # creates a horizontal strip of unblocked tiles from (x1,y) -> (x2,y)
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        # creates a vertical strip of unblocked tiles from (x,y1) -> (x,y2)
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

        
    def place_entities(self, room, entities, max_monsters_per_room):
        # Get a random number of monsters
        number_of_monsters = randint(0, max_monsters_per_room)

        for i in range(number_of_monsters):
            # Choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                if randint(0, 100) < 80:
                    monster = Entity(x , y, 'o', libtcod.desaturated_green, name = 'Orc', blocks = True)
                else:
                    monster = Entity(x, y, 'T', libtcod.darker_green, name = 'Troll', blocks = True)

                entities.append(monster)

    




