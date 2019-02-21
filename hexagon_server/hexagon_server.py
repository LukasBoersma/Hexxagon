#!/usr/bin/python3

from . import HexagonGame, RuleViolation
import socket
import re
from pprint import pprint, pformat

class HexagonServer:
    def __init__(self, player_count, timeout):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("localhost", 16823))
        self.listener.listen(5)

        self.game = HexagonGame()
        self.player_count = player_count
        self.timeout = timeout
        self.socket = [None] * player_count
        self.writer = [None] * player_count
        self.reader = [None] * player_count

    def send(self, player, cmd):
        self.writer[player-1].write(cmd+"\n")
        self.writer[player-1].flush()
    def read(self, player):
        return self.reader[player-1].readline().strip()
    def send_all(self, cmd):
        for player in [i for i in range(1, self.player_count+1)]:
            self.send(player, cmd)
    
    # Sends a message to all players except the one with the given id
    def send_others(self, player, cmd):
        other_players = [i for i in range(1, self.player_count+1) if i != player]
        for other_player in other_players:
            self.send(other_player, cmd)
    
    def wait_for_players(self):
        map_info = self.get_map_info()
        for player_id in range(1, self.player_count + 1):
            print("Waiting for player to connect to port 16823")
            (self.socket[player_id-1], address1) = self.listener.accept()
            self.reader[player_id-1] = self.socket[player_id-1].makefile('r')
            self.writer[player_id-1] = self.socket[player_id-1].makefile('w')
            self.send(player_id, "YOUR_ID %d" % player_id)
            self.send(player_id, map_info)

    def get_map_info(self):
        map = "MAP"
        for row in range(self.game.field_size_y):
            for col in range(self.game.field_size_x):
                pos = self.game.evenq_to_cube((col, row))
                (x,y,z) = pos
                value = self.game.get_field(pos)
                # Ignore invalid fields
                if value >= 0:
                    map += " %d %d %d %d" % (x, y, z, value)
        return map

    def print_map(self):
        for row in range(self.game.field_size_y):
            # Print odd columns
            for col in range(self.game.field_size_x):
                if col%2==0:
                    print("    ", end='')
                else:
                    pos = self.game.evenq_to_cube((col, row))
                    value = self.game.get_field(pos)
                    # Ignore invalid fields
                    if value >= 0:
                        print("%d   " % value, end='')
                    else:
                        print("    ", end='')
            print("")
            # Print even columns
            for col in range(self.game.field_size_x):
                if col%2!=0:
                    print("    ", end='')
                else:
                    pos = self.game.evenq_to_cube((col, row))
                    value = self.game.get_field(pos)
                    # Ignore invalid fields
                    if value >= 0:
                        print("%d   " % value, end='')
                    else:
                        print("    ", end='')
            print("")


    __REGEX_MOVE = re.compile(r'^MOVE (?P<x1>\-?[0-9]+) (?P<y1>\-?[0-9]+) (?P<z1>\-?[0-9]+) (?P<x2>\-?[0-9]+) (?P<y2>\-?[0-9]+) (?P<z2>\-?[0-9]+)$')

    def parse_cmd(self, player_id, cmd):

        if cmd is None:
            return False

        move_match = HexagonServer.__REGEX_MOVE.match(cmd)

        if move_match is None:
            return False

        x1 = int(move_match.group('x1'))
        y1 = int(move_match.group('y1'))
        z1 = int(move_match.group('z1'))
        x2 = int(move_match.group('x2'))
        y2 = int(move_match.group('y2'))
        z2 = int(move_match.group('z2'))

        self.game.move(player_id, (x1, y1, z1), (x2, y2, z2))
        return True

    def run(self):
        try:
            self.wait_for_players()

            winner = 0

            print("Initial map:")
            self.print_map()
            any_move_possible = True
            while True:
                if not any_move_possible:
                    print("Nobody can move. Exiting.")
                any_move_possible = False
                for player_id in range(1, self.player_count+1):
                    if not self.game.can_move(player_id):
                        self.send_all("PLAYER_CANT_MOVE")
                    else:
                        any_move_possible = True
                        cmd = self.read(player_id)
                        print("Received move from player %d: %s" % (player_id, cmd))

                        try:
                            cmd_parse_ok = self.parse_cmd(player_id, cmd)
                        except RuleViolation as violation:
                            self.send(player_id, "DISQUALIFIED rule violation "+pformat(violation))
                            winner = (player_id%self.player_count) + 1 # Player who would have next turn wins
                            print("Ending game because of rule violation")
                            break
                        if not cmd_parse_ok:
                            self.send(player_id, "DISQUALIFIED invalid command syntax")
                            winner = (player_id%self.player_count) + 1 # Player who would have next turn wins
                            print("Ending game because of rule violation")
                            break
                        
                    print("Map after player %d move:" % player_id)
                    self.print_map()

                    self.send_others(player_id, cmd)
                    map_info = self.get_map_info()
                    self.send_all(map_info)

                    winner = self.game.get_winner()

                    if winner != 0:
                        break
                if winner != 0:
                    break
            if winner == 0:
                print("Game ended with a draw" % winner)
                self.send_all("DRAW")
            else:
                print("Game ended, winner is %d" % winner)
                self.send_all("WINNER %d" % winner)
        finally:
            print("Exiting, closing all connections.")
            for socket in self.socket:
                socket.close()
            self.listener.close()
        