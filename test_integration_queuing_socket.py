import unittest
import socket

from multiprocessing import Process, Queue, Event

from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from udp_socket import UDPSocket

RECEIVER_PORT = 5001

class TestQueuerSocket(unittest.TestCase):
    def setUp(self) -> None:
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_list = [UWBTag("127.0.0.1", RECEIVER_PORT, "DD", [anchor_1, anchor_2]), UWBTag("127.0.0.1", RECEIVER_PORT, "EE", [anchor_1, anchor_2])]
        self.queuer = Queuer(tags_list, RandomStrategy())
        self.udp_socket = UDPSocket(5000, 2)

        self.ended = Event()
        self.timeout_counter = 0

    def receiver_process(self):
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver_socket.bind(("127.0.0.1", RECEIVER_PORT))
        receiver_socket.settimeout(.5)        

        while not self.ended.is_set():
            try:
                message_received, address = receiver_socket.recvfrom(1024)
                self.assertTrue(message_received == b'AA' or message_received == b'BB')
            except socket.timeout:
                timeout_counter += 1
            

    def test_queuing_multiprocess(self):
        q = Queue()
        p1 = Process(target=self.queuer.preparation_process, args=(q,))
        p2 = Process(target=self.udp_socket.sending_process, args=(q,))
        p3 = Process(target=self.receiver_process)

        p1.start()
        p2.start()

        p1.join()
        p2.join()
        self.ended.set()
        p3.join()

        self.assertEqual(self.timeout_counter, 0)




if __name__ == "__main__":
    unittest.main()
