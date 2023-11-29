import unittest

from multiprocessing import Queue, Manager

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
        tags_dict = {"FF": UWBTag("192.168.0.112", 7, "FF", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}
        dict_managed = Manager().dict(tags_dict)
        queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=8)

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(self.prepared_queue)

        self.assertEqual(self.prepared_queue.qsize(), 8)
        self.assertEqual(queuer.prepared_queue.qsize(), 0)

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
            queuer.results_decode(self.result_queue, self.decode_queue, dict_managed)

        tag = dict_managed["FF"]

        self.assertEqual(tag.distances_available, 5, f'Actual: {tag.distances_available}')
        self.assertEqual(self.prepared_queue.qsize(), 0)
        self.assertEqual(queuer.prepared_queue.qsize(), 0)

        queuer.queue_upper_limit = 4

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(self.prepared_queue)

        self.assertEqual(self.prepared_queue.qsize(), 4)

        while not self.prepared_queue.empty():
            message_encoded, ip, target_port = self.prepared_queue.get()
            print(message_encoded, ip, target_port)


            self.assertNotEqual(message_encoded.decode('utf-8'), "EE")

    def tearDown(self) -> None:
        print("Finished testing closest strategy integration")
        return super().tearDown()
            
if __name__ == '__main__':
    unittest.main()        
