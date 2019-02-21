#!/usr/bin/python3
import socket
import random
import re
from pprint import pprint

class HexagonRandomAi:
    def __init__(self, local_port=16824):
        self.socket = socket.create_connection(("localhost", 16823), 2, ("localhost", local_port))
        self.reader = self.socket.makefile('r')
        self.writer = self.socket.makefile('w')

    def send(self, cmd):
        self.writer.write(cmd+"\n")
        self.writer.flush()
    def read(self):
        line = self.reader.readline().strip()
        print("read line: '"+line+"'")
        return line

    def cube_distance(self, a, b):
        ax, ay, az = a
        bx, by, bz = b
        return int((abs(ax - bx) + abs(ay - by) + abs(az - bz)) / 2)
    
    __REGEX_YOUR_ID = re.compile(r'^YOUR_ID (?P<id>[0-9]+)$')
    __REGEX_MAP = re.compile(r'^MAP (?P<data>[0-9 \-]+)$')

    def read_my_id(self):
        cmd = self.read()
        match = HexagonRandomAi.__REGEX_YOUR_ID.match(cmd)
        if match is None:
            raise Exception("Expected YOUR_ID command, but got something else")
        else:
            self.my_id = int(match.group('id'))
            print("My player id: %d" % self.my_id)

    def read_cmd(self):
        cmd = self.read()
        match = HexagonRandomAi.__REGEX_MAP.match(cmd)
        if match is not None:
            map_data = match.group('data')
            v = map_data.split(' ')
            v = [int(x) for x in v]
            size = int(len(v)/4)
            self.map = [(v[i*4+0],v[i*4+1],v[i*4+2],v[i*4+3]) for i in range(size)]
        else:
            print("Ignoring unrecognized command: '"+cmd+"'")

    def do_move(self):
        random_map = self.map[:]
        random.shuffle(random_map)

        owned_fields = [(x,y,z,v) for (x,y,z,v) in random_map if v == self.my_id]
        if len(owned_fields) == 0:
            raise Exception("No own fields found")
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
        raise Exception("No valid moves found")


    def run(self):
        self.read_my_id()
        self.read_cmd()
        turn = 0
        while True:
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
