
FIELD_INVALID = -1
FIELD_EMPTY = 1
FIELD_PLAYER1 = 1
FIELD_PLAYER2 = 2

class Hexxagon:
    def __init__(self):

        self.field_size_x = 10
        self.field_size_y = 10

        self.__field = [[FIELD_EMPTY for i in range(10)] for i in range(10)]
        self.__field[0][0] = FIELD_PLAYER1
        self.__field[9][9] = FIELD_PLAYER2

        self.__surrounding_getters = [
            self.get_north_pos,
            self.get_northeast_pos,
            self.get_southeast_pos,
            self.get_south_pos,
            self.get_southwest_pos,
            self.get_northwest_pos
        ]
        
    def get_field(self, pos):
        x,y = pos
        return self.__field[x][y]

    def set_field(self, pos, new_value):
        x,y = pos
        self.__field[x][y] = new_value
    
    def pos_or_none(self, x,y):
        if x >= 0 and y >= 0 and x < self.field_size_x and y < self.field_size_y:
            return (x,y)
        else:
            return None

    def get_north_pos(self, x, y):
        return self.pos_or_none(x,y-1)
    
    def get_south_pos(self, x, y):
        return self.pos_or_none(x,y+1)

    def get_northeast_pos(self, x, y):
        if(x%2 == 0):
            return self.pos_or_none(x+1, y-1)
        else:
            return self.pos_or_none(x+1, y)

    def get_southeast_pos(self, x, y):
        if(x%2 == 0):
            return self.pos_or_none(x+1, y)
        else:
            return self.pos_or_none(x+1, y+1)

    def get_northwest_pos(self, x, y):
        if(x%2 == 0):
            return self.pos_or_none(x-1, y-1)
        else:
            return self.pos_or_none(x-1, y)

    def get_southwest_pos(self, x, y):
        if(x%2 == 0):
            return self.pos_or_none(x-1, y)
        else:
            return self.pos_or_none(x-1, y+1)

    def get_surrounding_positions(self, x,y):
        all_surroundings = [surrounding(x,y) for surrounding in self.__surrounding_getters]
        valid_surroundings = [pos for pos in all_surroundings if pos is not None]
        return valid_surroundings

    def get_other_player(self, player):
        return FIELD_PLAYER2 if player == FIELD_PLAYER1 else FIELD_PLAYER1

    def conquer_field(self, player, x, y):
        self.set_field((x, y), player)

        other_player = self.get_other_player(player)

        surrounding_positions = self.get_surrounding_positions(x,y)
        surroundings_of_other_player = [pos for pos in surrounding_positions if self.get_field(pos) == other_player]

        for pos in surroundings_of_other_player:
            self.set_field(pos, player)
