class Rect:
    def __init__(self, x, y, w, h):
        # Takes the x and y coordinates of the top left corner and then
        # computes the bottom right corner based on the w and h parameters.
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h


    def center(self):
        # Returns the center point of the rectangle as an (x,y) tuple.
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return(center_x, center_y)

    def intersect(self, other):
        # return true if this rectangle intersects with another one.
        return(self.x1 <= other.x2 and self.x2 >= other.x1 and
               self.y1 <= other.y2 and self.y2 >= other.y1)


    