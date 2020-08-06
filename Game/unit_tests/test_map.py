
import unittest 
from gameboard.map import GameMap

class TestGameMap(unittest.TestCase):
    def rest_load():
        game_map = GameMap.from_file('gameboard/map_demo.map')


if __name__ == '__main__':
    unittest.main()
