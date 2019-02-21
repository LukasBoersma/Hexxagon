#!/usr/bin/python3
import sys, os
from threading import Thread
from time import sleep

sys.path.insert(0, os.path.abspath('..'))
from hexagon_server import HexagonServer
from hexagon_random_ai.hexagon_random_ai import HexagonRandomAi

test_server_ready = False
local_client_port = 16824

def run_client():
    global local_client_port
    local_client_port += 1
    ai = HexagonRandomAi(local_port=local_client_port)
    ai.run()

def run_host():
    global test_server_ready
    server = HexagonServer(player_count=2, timeout=1000)
    sleep(0.1)
    test_server_ready = True
    server.run()

def test_randomai_match():
    thread_host = Thread(target = run_host)
    thread_host.start()

    global test_server_ready
    while not test_server_ready:
        sleep(0.1)

    thread_client1 = Thread(target = run_client)
    thread_client1.start()
    sleep(0.1)
    thread_client2 = Thread(target = run_client)
    thread_client2.start()

    thread_host.join()
    thread_client1.join()
    thread_client2.join()