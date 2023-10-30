import unittest
from queue import Queue
from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice

class TestQueuer(unittest.TestCase):
    def setUp(self) -> None:
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_list = [UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2]), UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2])]
        self.queuer = Queuer(tags_list, RandomStrategy())

    def test_encode_queue(self):
        self.queuer.encode_queue()
        queue_len = self.queuer.prepared_queue.qsize()

        self.assertGreater(queue_len, 0)
    
        self.assertIsInstance(self.queuer.prepared_queue.get(), tuple)

        queue_element = self.queuer.prepared_queue.get()

        # tuple should be (message, ip, port)
        self.assertIsInstance(queue_element[0], bytes)
        self.assertIsInstance(queue_element[1], str)
        self.assertIsInstance(queue_element[2], int)

    def test_fill_queue(self):
        q = Queue()
        self.queuer.encode_queue()

        self.queuer.fill_queue(q)
        self.assertGreaterEqual(q.qsize(), 3)
        self.assertLessEqual(q.qsize(), 5)

    def test_empty_throw(self):
        q = Queue()
        self.assertRaises(Exception, self.queuer.fill_queue, q)
        

if __name__ == "__main__":
    unittest.main()