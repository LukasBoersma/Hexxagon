#!/usr/bin/python3
import sys, os
from threading import Thread
from time import sleep
import unittest

sys.path.insert(0, os.path.abspath('..'))
from hexagon_server import HexagonGame

def make_game():
    return HexagonGame(field_radius=1)

def set_all_fields(game, value):
    for row in range(game.field_size_y):
        for col in range(game.field_size_x):
            pos = game.evenq_to_cube((col, row))
            if game.get_field(pos) != HexagonGame.FIELD_INVALID:
                game.set_field(pos, value)

class TestGameState(unittest.TestCase):

    def test_winning_state_1(self):
        game = make_game()
        set_all_fields(game, 1)
        self.assertEqual(game.get_winner(), 1)

    def test_winning_state_2(self):
        game = make_game()
        set_all_fields(game, 2)
        self.assertEqual(game.get_winner(), 2)

    def test_winning_state_no_winner(self):
        game = make_game()
        set_all_fields(game, 0)
        game.set_field((1,0,-1), 1)
        game.set_field((0,1,-1), 2)

        self.assertEqual(game.get_winner(), 0)

    def test_winning_state_draw(self):
        game = make_game()
        game.set_field((0,0,0), HexagonGame.FIELD_INVALID)
        game.set_field((1,0,-1), 1)
        game.set_field((1,-1,0), 1)
        game.set_field((0,-1,1), 1)
        game.set_field((-1,0,1), 2)
        game.set_field((-1,1,0), 2)
        game.set_field((0,1,-1), 2)
        self.assertEqual(game.get_winner(), -1)

if __name__ == '__main__':
    unittest.main()
