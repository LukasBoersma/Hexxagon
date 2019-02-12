from pprint import pprint

class RuleViolation(Exception):
    def __init__(self, move):
        self.move = move

class HexxagonGame:

    FIELD_INVALID = -1
    FIELD_EMPTY = 0
    FIELD_PLAYER1 = 1
    FIELD_PLAYER2 = 2

    NEIGHBOR_DIRECTIONS = [
        (+1, -1, 0), (+1, 0, -1), (0, +1, -1), 
        (-1, +1, 0), (-1, 0, +1), (0, -1, +1), 
    ]

    def __init__(self):

        field_radius = 4

        self.field_size_x = field_radius*2 + 1
        self.field_size_y = field_radius*2 + 1
        self.field_center_x = field_radius
        self.field_center_y = field_radius

        self.__field = [[HexxagonGame.FIELD_EMPTY for i in range(self.field_size_x)] for i in range(self.field_size_y)]

        # Make map into a "circle",
        # making fields invalid that are too far away from the center
        center = (0,0,0)
        for row in range(self.field_size_y):
            for col in range(self.field_size_x):
                pos = self.evenq_to_cube((col, row))
                if self.cube_distance(center, pos) > field_radius:
                    self.set_field(pos, HexxagonGame.FIELD_INVALID)
        
        # Initialize player start positions
        self.set_field((0, field_radius, -field_radius), HexxagonGame.FIELD_PLAYER1)
        self.set_field((field_radius, -field_radius, 0), HexxagonGame.FIELD_PLAYER1)
        self.set_field((-field_radius, 0, field_radius), HexxagonGame.FIELD_PLAYER1)

        self.set_field((field_radius, 0, -field_radius), HexxagonGame.FIELD_PLAYER2)
        self.set_field((0, -field_radius, field_radius), HexxagonGame.FIELD_PLAYER2)
        self.set_field((-field_radius, field_radius, 0), HexxagonGame.FIELD_PLAYER2)

    def __rule_assertion(self, rule, move_info):
        if not rule:
            raise RuleViolation(move_info)

    # https://www.redblobgames.com/grids/hexagons/
    def cube_to_evenq(self, cube_pos):
        x,y,z = cube_pos
        col = x
        row = int(z + (x + (x&1)) / 2)
        return (col+self.field_center_x, row+self.field_center_y)

    def evenq_to_cube(self, hex_pos):
        col,row = hex_pos
        col -= self.field_center_x
        row -= self.field_center_y
        x = col
        z = row - (col + (col&1)) / 2
        y = -x-z
        return (x, y, z)

    def cube_distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        return (abs(ax - bx) + abs(ay - by) + abs(az - bz)) / 2

    def get_field(self, pos):
        col,row = self.cube_to_evenq(pos)
        return self.__field[col][row]

    def set_field(self, pos, new_value):
        col,row = self.cube_to_evenq(pos)
        self.__field[col][row] = new_value
    
    def pos_or_none(self, pos):
        col,row = self.cube_to_evenq(pos)
        if col >= 0 and row >= 0 and col < self.field_size_x and row < self.field_size_y:
            return pos
        else:
            return None

    def get_neighbor_positions(self, pos):
        x,y,z = pos
        neighbors = [self.pos_or_none((x+dx, y+dy, z+dz)) for (dx, dy, dz) in HexxagonGame.NEIGHBOR_DIRECTIONS]
        valid_neighbors = [pos for pos in neighbors if pos is not None]
        return valid_neighbors

    def get_other_player(self, player):
        return HexxagonGame.FIELD_PLAYER2 if player == HexxagonGame.FIELD_PLAYER1 else HexxagonGame.FIELD_PLAYER1

    def conquer_field(self, player, pos):
        self.set_field(pos, player)

        other_player = self.get_other_player(player)

        neighbors_positions = self.get_neighbor_positions(pos)
        neighbors_of_other_player = [pos for pos in neighbors_positions if self.get_field(pos) == other_player]

        for pos in neighbors_of_other_player:
            self.set_field(pos, player)

    def move(self, player_id, from_pos, to_pos):
        player_on_that_field = self.get_field(from_pos)
        distance = self.cube_distance(from_pos, to_pos)

        # todo: assert that to_pos has distance <= two to from_pos
        self.__rule_assertion(player_id == player_on_that_field, ("move", from_pos, to_pos, "player does not occupy source field"))
        self.__rule_assertion(distance >= 1 and distance <= 3, ("move", from_pos, to_pos, "distance too small or too large"))

        if distance == 2:
            self.set_field(from_pos, HexxagonGame.FIELD_EMPTY)

        self.conquer_field(player_id, to_pos)
    
    def get_winner(self):
        count1 = 0
        count2 = 0
        for row in self.__field:
            for value in row:
                if value == HexxagonGame.FIELD_EMPTY:
                    return 0
                elif value == HexxagonGame.FIELD_PLAYER1:
                    count1 += 1
                elif value == HexxagonGame.FIELD_PLAYER2:
                    count2 += 1
        if count1 > count2:
            return 1
        else:
            return 2