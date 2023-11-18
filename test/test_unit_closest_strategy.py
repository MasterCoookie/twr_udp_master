import unittest

from multiprocessing import Queue

from positioning_functions import *
from closest_strategy import ClosestStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from queuer import Queuer

class TestClosestStrategy(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing closest strategy")

        self.anchor_1 = UWBDevice(None, None, "AA", 3, 4, 5)
        self.anchor_2 = UWBDevice(None, None, "BB", 2, 2, 2)
        self.anchor_3 = UWBDevice(None, None, "CC", 3, 3, 3)
        self.anchor_4 = UWBDevice(None, None, "DD", 0, 0, 1)
        self.anchor_5 = UWBDevice(None, None, "EE", 0, 0, .5)        
    
    def test_closest_strategy_triatelation_available(self):
        q = Queue()

        self.anchor_1.distance = 4.12
        self.anchor_2.distance = 5.91
        self.anchor_3.distance = 4.47
        self.anchor_4.distance = 8.6

        tags_dict = {"192.168.0.112": UWBTag("192.168.0.112", 7, "DD", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}
        tags_dict["192.168.0.112"].distances_available = 4

        queuer = Queuer(tags_dict, ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)

        queuer.encode_queue()
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 4)

        while not q.empty():
            message_encoded, ip, target_port = q.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

            message_decoded = message_encoded.decode('utf-8')

            self.assertNotEqual(message_decoded, "EE")
