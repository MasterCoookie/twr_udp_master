import unittest

from multiprocessing import Queue

from closest_strategy import ClosestStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from queuer import Queuer

class TestClosestStrategy(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing closest strategy integration")

        self.anchor_1 = UWBDevice(None, None, "AA", 3, 4, 5)
        self.anchor_2 = UWBDevice(None, None, "BB", 2, 2, 2)
        self.anchor_3 = UWBDevice(None, None, "CC", 3, 3, 3)
        self.anchor_4 = UWBDevice(None, None, "DD", 0, 0, 1)
        self.anchor_5 = UWBDevice(None, None, "EE", 0, 0, .5)

        self.prepared_queue = Queue()
        self.result_queue = Queue()
        self.decode_queue = Queue()

        return super().setUp()
    
    def test_closest_starting(self):
        tags_dict = {"192.168.0.112": UWBTag("192.168.0.112", 7, "FF", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}

        queuer = Queuer(tags_dict, ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=8)

        queuer.encode_queue()
        queuer.fill_queue(self.prepared_queue)

        self.assertEqual(self.prepared_queue.qsize(), 8)

        fake_restults = [4.12, 5.91, 4.47, 8.6, 8.85]
        i = 0
        while not self.prepared_queue.empty():
            message_encoded, ip, target_port = self.prepared_queue.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

            message_decoded = message_encoded.decode('utf-8')

            message_decoded = f'DIST {message_decoded}: {fake_restults[i]}m'

            self.result_queue.put((ip, message_decoded.encode(), (ip, target_port)))

            i += 1
            if i == 5:
                i = 0

        while not self.result_queue.empty():
            queuer.results_decode(self.result_queue, self.decode_queue)

        tag = tags_dict["192.168.0.112"]

        self.assertEqual(tag.distances_available, 5)
        self.assertEqual(self.prepared_queue.qsize(), 0)

        queuer.encode_queue()
        queuer.fill_queue(self.prepared_queue)

        self.assertEqual(self.prepared_queue.qsize(), 8)

        while not self.prepared_queue.empty():
            message_encoded, ip, target_port = self.prepared_queue.get()
            print(message_encoded, ip, target_port)


            

        
