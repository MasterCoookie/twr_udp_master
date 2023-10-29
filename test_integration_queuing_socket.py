import unittest

from queue import Queue
from multiprocessing import Process

from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice

class TestQueuer(unittest.TestCase):
    def setUp(self) -> None:
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_list = [UWBTag("127.0.0.1", 7, "DD", [anchor_1, anchor_2]), UWBTag("127.0.0.1", 7, "EE", [anchor_1, anchor_2])]
        self.queuer = Queuer(tags_list, RandomStrategy())

    def test_queuing_multiprocess(self):
        q = Queue()
        messages_count = 0
        while messages_count < 10:
            pass

if __name__ == "__main__":
    unittest.main()
