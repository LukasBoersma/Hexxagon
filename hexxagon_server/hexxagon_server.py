from hexxagon_game import HexxagonGame

import socket
import re

class HexxagonServer:
    def __init__(self):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listener.bind(("localhost", 80))
        self.listener.listen(5)
    
    def wait_for_players(self):
        (self.p1_socket, address) = self.listener.accept()
        (self.p2_socket, address) = self.listener.accept()
        self.p1_socket.send("YOUR_ID 1")
        self.p2_socket.send("YOUR_ID 2")

    __REGEX_MOVE = re.compile(r'^MOVE ([0-9]+) ([0-9]+) ([0-9]+) ([0-9]+)$')

    def parse_cmd(self, player_id, cmd):
        pass

    def run(self):
        self.wait_for_players()

        while True:
            cmd_p1 = self.p1_socket.recv()
            self.parse_cmd(1, cmd_p1)
            cmd_p2 = self.p2_socket.recv()
            self.parse_cmd(2, cmd_p2)