import unittest

from complete_random_strategy import CompleteRandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from queuer import Queuer

class TestQueuer(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing complete random strategy")
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_dict = {"192.168.0.112": UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2]), "192.168.0.113": UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2])}
        self.queuer = Queuer(tags_dict, CompleteRandomStrategy())
    
    def test_prepare_queue(self):
        self.queuer.encode_queue()
        self.queuer.prepare_queue(self.queuer.tags_dict)
        self.assertGreaterEqual(self.queuer.prepared_queue.qsize(), 2)