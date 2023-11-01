import unittest
import time
from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from multiprocessing import Event, Process, Queue

class TestQueuer(unittest.TestCase):
    def setUp(self) -> None:
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_list = [UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2]), UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2])]
        self.queuer = Queuer(tags_list, RandomStrategy())

    def check_queue_contents(self, queue):
        while not queue.empty():
            message_encoded, ip, target_port = queue.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

    def test_encode_queue(self):
        self.queuer.encode_queue()
        queue_len = self.queuer.prepared_queue.qsize()

        self.assertGreater(queue_len, 0)
    
        self.assertIsInstance(self.queuer.prepared_queue.get(), tuple)

        self.check_queue_contents(self.queuer.prepared_queue)

    def test_fill_queue(self):
        q = Queue()
        self.queuer.encode_queue()

        self.queuer.fill_queue(q)
        self.assertGreaterEqual(q.qsize(), 3)
        self.assertLessEqual(q.qsize(), 5)

    def test_empty_throw(self):
        q = Queue()
        self.assertRaises(Exception, self.queuer.fill_queue, q)

    def test_queing_process(self):
        q = Queue()
        ended = Event()
        ended.clear()

        p1 = Process(target=self.queuer.queing_process, args=(ended, q))
        p1.start()

        time.sleep(.25)
        q.get()
        q.get()
        time.sleep(.25)
        q.get()
        q.get()
        time.sleep(.25)

        ended.set()
        p1.join()

        self.assertGreaterEqual(q.qsize(), 3)
        self.assertLessEqual(q.qsize(), 5)

        self.check_queue_contents(q)
        

if __name__ == "__main__":
    unittest.main()