#!/usr/bin/python3
import socket
import random
import re
from pprint import pprint

class HexagonRandomAi:
    def __init__(self, local_port=None):
        timeout = 60
        self.running = True

        if local_port is None:
            self.socket = socket.create_connection(("localhost", 16823), timeout)
        else:
            self.socket = socket.create_connection(("localhost", 16823), timeout, ("localhost", local_port))

        self.reader = self.socket.makefile('r')
        self.writer = self.socket.makefile('w')

    def send(self, cmd):
        self.writer.write(cmd+"\n")
        self.writer.flush()
    def read(self):
        line = self.reader.readline()
        if line is None or len(line) == 0:
            print("Failed to read from server. Stopping.")
            self.running = False
            return None

        line = line.strip()
        return line

    def cube_distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        return int((abs(ax - bx) + abs(ay - by) + abs(az - bz)) / 2)
    
    __REGEX_YOUR_ID = re.compile(r'^YOUR_ID (?P<id>[0-9]+)$')
    __REGEX_WINNER = re.compile(r'^WINNER (?P<id>[0-9]+)$')
    __REGEX_MAP = re.compile(r'^MAP (?P<data>[0-9 \-]+)$')
    __REGEX_MOVE = re.compile(r'^MOVE (?P<x1>\-?[0-9]+) (?P<y1>\-?[0-9]+) (?P<z1>\-?[0-9]+) (?P<x2>\-?[0-9]+) (?P<y2>\-?[0-9]+) (?P<z2>\-?[0-9]+)$')

    def read_my_id(self):
        cmd = self.read()
        if cmd is None:
            return

        match = HexagonRandomAi.__REGEX_YOUR_ID.match(cmd)
        if match is None:
            raise Exception("Expected YOUR_ID command, but got something else")
        else:
            self.my_id = int(match.group('id'))
            print("My player id: %d" % self.my_id)

    def read_cmd(self):
        cmd = self.read()
        if cmd is None:
            return
        
        map_match = HexagonRandomAi.__REGEX_MAP.match(cmd)
        if map_match is not None:
            map_data = map_match.group('data')
            v = map_data.split(' ')
            v = [int(x) for x in v]
            size = int(len(v)/4)
            self.map = [(v[i*4+0],v[i*4+1],v[i*4+2],v[i*4+3]) for i in range(size)]
        elif HexagonRandomAi.__REGEX_WINNER.match(cmd) is not None:
            print("Game ended.")
            self.running = False
        elif HexagonRandomAi.__REGEX_MOVE.match(cmd) is not None:
            return # Ignore move commands from server
        else:
            # Print a warning when receiving anything other than above
            print("Warning: Ignoring unrecognized command: '"+cmd+"'")

    def do_move(self):
        random_map = self.map[:]
        random.shuffle(random_map)

        owned_fields = [(x,y,z,v) for (x,y,z,v) in random_map if v == self.my_id]
        if len(owned_fields) == 0:
            print("No owned fields found!")
            return
        for owned_field in owned_fields:
            (x,y,z,v) = owned_field
            pos = (x,y,z)
            valid_neighbors = [(x2,y2,z2,v2) for (x2,y2,z2,v2) in random_map if v2 == 0 and self.cube_distance(pos, (x2, y2, z2)) in [1,2]]
            if len(valid_neighbors) == 0:
                continue
            else:
                (x2,y2,z2,v2) = valid_neighbors[0]
                self.send("MOVE %d %d %d %d %d %d" % (x, y, z, x2, y2, z2))
                return
        # Read "player_cant_move"
        print("No valid move available. Skipping my turn.")
        self.read_cmd()


    def run(self):
        try:
            self.read_my_id()
            self.read_cmd()
            turn = 0
            print("Starting HexagonRandomAi")
            while self.running:
                turn = (turn)%2 + 1
                if turn == self.my_id:
                    self.do_move()
                    # Read map
                    self.read_cmd()
                else:
                    # Read move
                    self.read_cmd()
                    # Read map
                    self.read_cmd()
        finally:
            print("Closing connection to server.")
            self.socket.close()