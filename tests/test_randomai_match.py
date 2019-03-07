#!/usr/bin/python3
import sys, os
from threading import Thread
from time import sleep
import unittest

sys.path.insert(0, os.path.abspath('..'))
from hexagon_server import HexagonServer
from hexagon_random_ai.hexagon_random_ai import HexagonRandomAi
from hexagon_simple_ai.hexagon_simple_ai import HexagonSimpleAi

test_server_ready = False

def run_random_client():
    ai = HexagonRandomAi()
    ai.run()

def run_simple_client():
    ai = HexagonSimpleAi()
    ai.run()

def run_host():
    global test_server_ready
    server = HexagonServer(player_count=2, timeout=1000)
    test_server_ready = True
    server.run()

class TestRandomAiMatch(unittest.TestCase):
    def test_randomai_match(self):
        thread_host = Thread(target = run_host)
        thread_host.start()

        global test_server_ready
        while not test_server_ready:
            sleep(0.1)

        sleep(0.5)

        thread_client1 = Thread(target = run_random_client)
        thread_client1.start()
        sleep(0.1)
        thread_client2 = Thread(target = run_random_client)
        thread_client2.start()

        thread_host.join()
        thread_client1.join()
        thread_client2.join()


class TestSimpleVsRandomAiMatch(unittest.TestCase):
    def test_randomai_match(self):
        thread_host = Thread(target = run_host)
        thread_host.start()

        global test_server_ready
        while not test_server_ready:
            sleep(0.1)

        thread_client1 = Thread(target = run_simple_client)
        thread_client1.start()
        sleep(0.1)
        thread_client2 = Thread(target = run_random_client)
        thread_client2.start()

        thread_host.join()
        thread_client1.join()
        thread_client2.join()