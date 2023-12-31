import unittest
import time
from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from multiprocessing import Event, Process, Queue, Manager

class TestQueuer(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing queuer")
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_dict = {"192.168.0.112": UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2]), "192.168.0.113": UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2])}
        self.dict_managed = Manager().dict(tags_dict)
        self.queuer = Queuer(RandomStrategy())

    def check_queue_contents(self, queue):
        while not queue.empty():
            message_encoded, ip, target_port = queue.get()

            self.assertIsInstance(message_encoded, bytes)
            self.assertIsInstance(ip, str)
            self.assertIsInstance(target_port, int)

    def test_encode_queue(self):
        self.queuer.encode_queue(self.dict_managed)
        queue_len = self.queuer.prepared_queue.qsize()

        self.assertGreater(queue_len, 0)
    
        self.assertIsInstance(self.queuer.prepared_queue.get(), tuple)

        self.check_queue_contents(self.queuer.prepared_queue)

    def test_fill_queue(self):
        q = Queue()
        self.queuer.encode_queue(self.dict_managed)

        self.queuer.fill_queue(q)
        self.assertGreaterEqual(q.qsize(), 3)
        self.assertLessEqual(q.qsize(), 5)

        time.sleep(.001)
        q.close()

    def test_empty_throw(self):
        q = Queue()
        self.assertRaises(Exception, self.queuer.fill_queue, q)
        time.sleep(.001)
        q.close()

    def test_queing_process(self):
        q = Queue()
        ended = Event()
        ended.clear()

        p1 = Process(target=self.queuer.queing_process, args=(ended, q, self.dict_managed))
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

        self.assertGreater(q.qsize(), 0)
        self.assertLessEqual(q.qsize(), 5)

        self.check_queue_contents(q)

        time.sleep(.001)
        q.close()

    def test_results_decode(self):
        results_q = Queue()
        for i in range(2):
            results_q.put(('192.168.0.112', f'Hello World{i}'.encode('utf-8'), ('192.168.0.112', 5001)))
            results_q.put(('192.168.0.113', f'Hello World{i}'.encode('utf-8'), ('192.168.0.113', 5001)))
        
        while not results_q.empty():
            self.queuer.results_decode(results_q.get(), self.dict_managed)

        results_q.close()

    def tearDown(self):
        print("Finished testing queuer")


    def test_generate_dict(self):
        tags = {
            'AA': ('127.0.0.1', 5001, [('BB', 1, 1, 1), ('CC', 2, 2, 2)]),
            'DD': ('127.0.0.2', 5002, [('EE', 3, 3, 3), ('FF', 4, 5, 6), ('GG', .5, .5, .5)])
        }
        queuer = Queuer(None, RandomStrategy())
        generated = queuer.generate_dict(tags)

        self.assertEqual(len(generated), 2)

        self.assertIsInstance(generated['AA'], UWBTag)
        self.assertIsInstance(generated['DD'], UWBTag)

        self.assertEqual(generated['AA'].available_devices[0].x_pos, 1)
        self.assertEqual(generated['AA'].available_devices[1].x_pos, 2)
        self.assertEqual(generated['DD'].available_devices[0].y_pos, 3)
        self.assertEqual(generated['DD'].available_devices[1].z_pos, 6)
        self.assertEqual(generated['DD'].available_devices[2].z_pos, .5)

        self.assertIsInstance(generated['AA'].available_devices[0], UWBDevice)
        self.assertIsInstance(generated['AA'].available_devices[1], UWBDevice)
        self.assertIsInstance(generated['DD'].available_devices[0], UWBDevice)
        self.assertIsInstance(generated['DD'].available_devices[1], UWBDevice)

        self.assertEqual(generated['AA'].ip, '127.0.0.1')
        self.assertEqual(generated['AA'].device_port, 5001)
        self.assertEqual(generated['DD'].ip, '127.0.0.2')
        self.assertEqual(generated['DD'].device_port, 5002)

        self.assertEqual(generated['AA'].available_devices[0].uwb_address, 'BB')
        self.assertEqual(generated['AA'].available_devices[1].uwb_address, 'CC')
        self.assertEqual(generated['DD'].available_devices[0].uwb_address, 'EE')
        self.assertEqual(generated['DD'].available_devices[1].uwb_address, 'FF')

    def test_results_decode(self):
        results_q = Queue()
        for i in range(2):
            results_q.put(('127.0.0.1', f'Hello World{i}'.encode('utf-8'), ('127.0.0.1', 5001)))
        
        decoded_q = Queue()
        self.queuer.results_decode(results_q, decoded_q, self.dict_managed)

        self.assertEqual(decoded_q.qsize(), 2)

        i = 0
        while not decoded_q.empty():
            q_element = decoded_q.get()
            self.assertIsInstance(q_element, tuple)
            self.assertEqual(len(q_element), 2)
            self.assertEqual(q_element[0], '127.0.0.1')
            self.assertEqual(q_element[1], f'Hello World{i}')
            i += 1



if __name__ == "__main__":
    unittest.main()