from hexxagon_game import HexxagonGame

import socket
import re
from pprint import pprint

class HexxagonServer:
    def __init__(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("localhost", 16823))
        self.listener.listen(5)

        self.game = HexxagonGame()

    def send1(self, cmd):
        self.p1_writer.write(cmd+"\n")
    def send2(self, cmd):
        self.p2_writer.write(cmd+"\n")
    def read1(self):
        self.p1_reader.readline()
    def read2(self):
        self.p2_reader.readline()
    
    def wait_for_players(self):
        (socket1, address1) = self.listener.accept()
        (socket2, address2) = self.listener.accept()
        self.p1_reader = socket1.makefile('r')
        self.p2_reader = socket2.makefile('r')
        self.p1_writer = socket1.makefile('w')
        self.p2_writer = socket2.makefile('w')
        map_info = self.get_map_info()
        self.send1("YOUR_ID 1")
        self.send1(map_info)
        self.send2("YOUR_ID 2")
        self.send2(map_info)

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

    __REGEX_MOVE = re.compile(r'^MOVE (?P<x1>[0-9]+) (?P<y1>[0-9]+) (?P<z1>[0-9]+) (?P<x2>[0-9]+) (?P<y2>[0-9]+) (?P<z2>[0-9]+)$')

    def parse_cmd(self, player_id, cmd):
        print(">>>>>>>>>>>>>>>")
        pprint(player_id)
        pprint(cmd)

        if cmd is None:
            return False

        move_match = HexxagonServer.__REGEX_MOVE.match(cmd)

        if move_match is None:
            return False

        x1 = move_match.group('x1')
        y1 = move_match.group('y1')
        z1 = move_match.group('z1')
        x2 = move_match.group('x2')
        y2 = move_match.group('y2')
        z2 = move_match.group('z2')

        self.game.move(player_id, (x1, y1, z1), (x2, y2, z2))
        return True

    def run(self):
        self.wait_for_players()

        winner = 0

        while True:
            cmd_p1 = self.read1()
            move1_ok = self.parse_cmd(1, cmd_p1)
            
            if not move1_ok:
                self.send1("DISQUALIFIED invalid move")
                winner = 2
                break
            
            self.send2(cmd_p1)

            winner = self.game.get_winner()

            if winner != 0:
                break

            cmd_p2 = self.read2()
            move2_ok = self.parse_cmd(2, cmd_p2)

            if not move2_ok:
                self.send2("DISQUALIFIED invalid move")
                winner = 1
                break

            self.send1(cmd_p2)

            winner = self.game.get_winner()

            if winner != 0:
                break
        
        self.send1("WINNER %d" % winner)
        self.send2("WINNER %d" % winner)
        