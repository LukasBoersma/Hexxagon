#!/usr/bin/python3
from hexagon_random_ai.hexagon_random_ai import HexagonRandomAi
import random

random_port = random.randint(10823, 16822)

ai = HexagonRandomAi(local_port=random_port)
ai.run()