from map_objects.tile import Tile

class GameMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

    def initialize_tiles(self):
        # Generate a 2d arary unblocked tiles that fill our map.
        tiles = [[Tile(False) for y in range(self.height)] for x in range(self.width)]

        # Buld some blocked tiles that are blocked (and with blocked sight).
        tiles[30][22].blocked = True
        tiles[30][22].block_sight = True
        tiles[31][22].blocked = True
        tiles[31][22].block_sight = True
        tiles[32][22].blocked = True
        tiles[32][22].block_sight = True

        return tiles

    def is_blocked(self, x, y):
        # Returns true if tile is blocked, returns false otherwise.
        if self.tiles[x][y].blocked:
            return True
        
        return False
