import unittest
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

    def test_prepare_queue(self):
        self.queuer.queuing_strategy.prepare_queue(self.queuer.tags_list)
        queue_len = self.queuer.queuing_strategy.prepared_queue.qsize()

        #TODO - len shpould be based on smth
        self.assertEqual(2, queue_len)
    
        self.assertIsInstance(self.queuer.queuing_strategy.prepared_queue.get(), tuple)

        queue_element = self.queuer.queuing_strategy.prepared_queue.get()
        self.assertIsInstance(queue_element[0], UWBTag)
        self.assertIsInstance(queue_element[1], UWBDevice)

if __name__ == "__main__":
    unittest.main()