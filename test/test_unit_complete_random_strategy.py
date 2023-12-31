import unittest

from multiprocessing import Queue, Manager

from complete_random_strategy import CompleteRandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from queuer import Queuer

class TestCompleteRandomStrategy(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing complete random strategy")
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_dict = {"192.168.0.112": UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2]), "192.168.0.113": UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2])}
        self.tags_managed = Manager().dict(tags_dict)
        self.queuer = Queuer(CompleteRandomStrategy(), queue_lower_limit=4, queue_upper_limit=4)
    
    def check_queue_contents(self, queue):
        messages = []

        while not queue.empty():
            message_encoded, ip, target_port = queue.get()

            print(message_encoded, ip, target_port)

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

            messages.append(message_encoded.decode())

        self.assertEqual(messages.count("AA"), 2)
        self.assertEqual(messages.count("BB"), 2)

    
    def test_prepare_queue(self):
        q = Queue()

        self.queuer.encode_queue(self.tags_managed)
        self.queuer.fill_queue(q)
        self.assertEqual(q.qsize(), 4)
        self.check_queue_contents(q)
