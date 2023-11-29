import unittest

from multiprocessing import Queue, Manager

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
        print("Testing closest strategy trilateration available")
        q = Queue()

        self.anchor_1.distance = 4.12
        self.anchor_2.distance = 5.91
        self.anchor_3.distance = 4.47
        self.anchor_4.distance = 8.6

        tags_dict = {"FF": UWBTag("192.168.0.112", 7, "FF", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}
        tags_dict["FF"].distances_available = 4

        dict_managed = Manager().dict(tags_dict)
        queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 4)

        while not q.empty():
            message_encoded, ip, target_port = q.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

            message_decoded = message_encoded.decode('utf-8')

            self.assertNotEqual(message_decoded, "EE")
        print("managed:", dict_managed)
        self.assertEqual(dict_managed["FF"].distances_available, 4)

    def test_closest_strategy_triatelation_not_available(self):
        print("Testing closest strategy trilateration not available")
        q = Queue()
        tags_dict = {"FF": UWBTag("192.168.0.112", 7, "DD", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}
        dict_managed = Manager().dict(tags_dict)
        queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=5)

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 5)

        self.assertEqual(q.get()[0].decode('utf-8'), "AA")
        self.assertEqual(q.get()[0].decode('utf-8'), "BB")
        self.assertEqual(q.get()[0].decode('utf-8'), "CC")
        self.assertEqual(q.get()[0].decode('utf-8'), "DD")
        self.assertEqual(q.get()[0].decode('utf-8'), "EE")


    def test_closest_strategy_decode(self):
        print("Testing closest strategy decode")
        tags_dict = {"FF": UWBTag("192.168.0.112", 7, "FF", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}
        dict_managed = Manager().dict(tags_dict)
        queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)

        result_q = Queue()
        decoded_q = Queue()

        result_q.put(('192.168.0.112', b'DIST FF to AA: 4.12m', ('192.168.0.112', 7)))
        result_q.put(('192.168.0.112', b'DIST FF to BB: 5.91m', ('192.168.0.112', 7)))
        result_q.put(('192.168.0.112', b'DIST FF to CC: 4.47m', ('192.168.0.112', 7)))
        result_q.put(('192.168.0.112', b'DIST FF to DD: 8.6m', ('192.168.0.112', 7)))

        queuer.results_decode(result_q, decoded_q, dict_managed)

        tags = dict_managed["FF"]

        self.assertEqual(decoded_q.qsize(), 4)
        self.assertEqual(tags.distances_available, 4)
        self.assertAlmostEqual(float(tags.available_devices[0].distance), 4.12, delta=0.05)
        self.assertAlmostEqual(float(tags.available_devices[1].distance), 4.47, delta=0.05)
        self.assertAlmostEqual(float(tags.available_devices[2].distance), 5.91, delta=0.05)
        self.assertAlmostEqual(float(tags.available_devices[3].distance), 8.6, delta=0.05)

    def test_queue_topping(self):
        print("Testing closest strategy queue topping")
        q = Queue()
        tags_dict = {"FF": UWBTag("192.168.0.112", 7, "FF", [self.anchor_1, self.anchor_2, self.anchor_3, self.anchor_4, self.anchor_5])}
        dict_managed = Manager().dict(tags_dict)
        queuer = Queuer(ClosestStrategy(), queue_lower_limit=4, queue_upper_limit=4)

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 4)
        self.assertEqual(queuer.queuing_strategy.prepared_queue.qsize(), 0)

        self.assertEqual(q.get()[0].decode('utf-8'), "AA")

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 3)
        self.assertEqual(queuer.queuing_strategy.prepared_queue.qsize(), 0)

        self.assertEqual(q.get()[0].decode('utf-8'), "BB")
        self.assertEqual(q.get()[0].decode('utf-8'), "CC")

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 1)
        self.assertEqual(queuer.queuing_strategy.prepared_queue.qsize(), 0)

        self.assertEqual(q.get()[0].decode('utf-8'), "DD")

        queuer.encode_queue(dict_managed)
        queuer.fill_queue(q)

        self.assertEqual(q.qsize(), 4)
        self.assertEqual(queuer.queuing_strategy.prepared_queue.qsize(), 0)

        occurred = []
        while not q.empty():
            message_encoded, ip, target_port = q.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

            message_decoded = message_encoded.decode('utf-8')

            if message_decoded not in occurred:
                occurred.append(message_decoded)
            else:
                self.fail("Duplicate message in queue")

            print(message_decoded)

if __name__ == "__main__":
    unittest.main()