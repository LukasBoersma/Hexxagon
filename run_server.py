#!/usr/bin/python3
from hexagon_server import HexagonServer

server = HexagonServer(player_count=2, timeout=1000)
server.run()