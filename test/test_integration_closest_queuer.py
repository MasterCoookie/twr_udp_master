import unittest

from multiprocessing import Queue

from closest_strategy import ClosestStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from queuer import Queuer

class TestClosestStrategy(unittest.TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_closest_starting(self):
        pass
