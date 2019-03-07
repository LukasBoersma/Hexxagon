#!/usr/bin/python3
import socket
import random
import re
import math
from pprint import pprint
import sys
import os

sys.path.insert(0, os.path.abspath('..'))
from hexagon_server import HexagonGame

class HexagonSimpleAi:
    def __init__(self):
        timeout = 60
        self.running = True

        self.socket = socket.socket()
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.connect(("localhost", 16823))

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

    def simulate_move(self, current_map, source_field, target_field):
        (sx, sy, sz, sv) = source_field
        (tx, ty, tz, tv) = target_field

        source_player = sv
        source_pos = (sx, sy, sz)
        target_pos = (tx, ty, tz)
        resulting_map = current_map[:] #create a copy of the map
        for i in range(len(resulting_map)):
            (x, y, z, v) = resulting_map[i]
            pos = (x, y, z)
            if pos == source_field:
                v = 0
            elif pos == source_pos or self.cube_distance(pos, target_pos) == 1:
                v = source_player
            resulting_map[i] = (x, y, z, v)
        return resulting_map

    def get_score(self, scored_map, scored_player):
        counts = [0 for i in range(3)]
        for (x, y, z, v) in scored_map:
            counts[v] += 1
        
        if counts[0] == 0:
            if counts[1] > counts[2]:
                return math.inf if scored_player == 1 else -math.inf
            elif counts[2] > counts[1]:
                return math.inf if scored_player == 2 else -math.inf
            else:
                return 0
        else:
            player1_factor = 1 if scored_player == 1 else -1
            return (counts[1] - counts[2]) * player1_factor


    def read_my_id(self):
        cmd = self.read()
        if cmd is None:
            return

        match = HexagonSimpleAi.__REGEX_YOUR_ID.match(cmd)
        if match is None:
            raise Exception("Expected YOUR_ID command, but got something else")
        else:
            self.my_id = int(match.group('id'))
            print("My player id: %d" % self.my_id)

    def read_cmd(self):
        cmd = self.read()
        if cmd is None:
            return
        
        map_match = HexagonSimpleAi.__REGEX_MAP.match(cmd)
        if map_match is not None:
            map_data = map_match.group('data')
            v = map_data.split(' ')
            v = [int(x) for x in v]
            size = int(len(v)/4)
            self.map = [(v[i*4+0],v[i*4+1],v[i*4+2],v[i*4+3]) for i in range(size)]
        elif HexagonSimpleAi.__REGEX_WINNER.match(cmd) is not None:
            print("Game ended.")
            self.running = False
        elif HexagonSimpleAi.__REGEX_MOVE.match(cmd) is not None:
            return # Ignore move commands from server
        else:
            # Print a warning when receiving anything other than above
            print("Warning: Ignoring unrecognized command: '"+cmd+"'")

    def do_move(self):

        owned_fields = [(x,y,z,v) for (x,y,z,v) in self.map if v == self.my_id]
        if len(owned_fields) == 0:
            print("No owned fields found!")
            return

        possible_moves = []

        for owned_field in owned_fields:
            (x,y,z,v) = owned_field
            pos = (x,y,z)
            valid_neighbors = [(x2,y2,z2,v2) for (x2,y2,z2,v2) in self.map if v2 == 0 and self.cube_distance(pos, (x2, y2, z2)) in [1,2]]
            if len(valid_neighbors) == 0:
                continue # Cannot do any moves from that field
            else:
                # Every entry in valid_neighbors represents a valid move.
                for target_field in valid_neighbors:
                    possible_moves.append((owned_field, target_field))

        if len(possible_moves) == 0:
            # Read "player_cant_move"
            print("No valid move available. Skipping my turn.")
            self.read_cmd()

        # Add randomness by shuffling moves.
        # If there are multiple moves with the same score, will result in a random selection of those.
        random.shuffle(possible_moves)

        best_score = -math.inf
        best_move = possible_moves[0]

        print("Considering %d possible moves" % len(possible_moves))

        # Evaluate all moves
        for move in possible_moves:
            source, target = move
            score = self.get_score(self.simulate_move(self.map, source, target), self.my_id)
            if score > best_score:
                best_score = score
                best_move = move

        # Send the best found move
        (x, y, z, v), (x2, y2, z2, v2) = move
        self.send("MOVE %d %d %d %d %d %d" % (x, y, z, x2, y2, z2))

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