import unittest
import time
from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from multiprocessing import Event, Process, Queue

class TestQueuer(unittest.TestCase):
    def setUp(self) -> None:
        print("Testing queuer")
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_dict = {"192.168.0.112": UWBTag("192.168.0.112", 7, "DD", [anchor_1, anchor_2]), "192.168.0.113": UWBTag("192.168.0.113", 7, "EE", [anchor_1, anchor_2])}
        self.queuer = Queuer(tags_dict, RandomStrategy())

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

        time.sleep(.001)
        q.close()

    def test_results_decode(self):
        results_q = Queue()
        for i in range(2):
            results_q.put(('192.168.0.112', f'Hello World{i}'.encode('utf-8'), ('192.168.0.112', 5001)))
            results_q.put(('192.168.0.113', f'Hello World{i}'.encode('utf-8'), ('192.168.0.113', 5001)))
        
        while not results_q.empty():
            self.queuer.results_decode(results_q.get())

        results_q.close()

    def tearDown(self):
        print("Finished testing queuer")


    def test_generate_dict(self):
        tags = {
            'AA': ('127.0.0.1', 5001, ['BB',  'CC']),
            'DD': ('127.0.0.2', 5002, ['EE', 'FF', 'GG'])
        }
        queuer = Queuer(None, RandomStrategy())
        generated = queuer.generate_dict(tags)

        self.assertEqual(len(generated), 2)

        self.assertIsInstance(generated['AA'], UWBTag)
        self.assertIsInstance(generated['DD'], UWBTag)

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


if __name__ == "__main__":
    unittest.main()