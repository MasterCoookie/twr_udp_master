import unittest
import time

from multiprocessing import Process, Queue, Event

from queuer import Queuer
from random_startegy import RandomStrategy
from uwb_tag import UWBTag
from uwb_device import UWBDevice
from udp_socket import UDPSocket
from helper_functions import receiver_process

RECEIVER_PORT = 5001

class TestQueuerSocket(unittest.TestCase):
    def setUp(self) -> None:
        anchor_1 = UWBDevice(None, None, "AA")
        anchor_2 = UWBDevice(None, None, "BB")
        tags_list = [UWBTag("127.0.0.1", RECEIVER_PORT, "DD", [anchor_1, anchor_2]), UWBTag("127.0.0.1", RECEIVER_PORT, "EE", [anchor_1, anchor_2])]
        self.queuer = Queuer(tags_list, RandomStrategy())
        self.udp_socket = UDPSocket(5000, 2)

        self.timeout_counter = 0            

    def test_queuing_multiprocess(self):
        msg_q = Queue()
        result_q = Queue()

        ended = Event()
        ended.clear()

        p1 = Process(target=self.queuer.queing_process, args=(ended, msg_q))
        p2 = Process(target=self.udp_socket.sending_process, args=(ended, msg_q, result_q))
        p3 = Process(target=receiver_process, args=(ended, ))

        p1.start()
        time.sleep(.1)
        p2.start()
        p3.start()

        time.sleep(.5)
        ended.set()

        p1.join()
        p2.join()
        p3.join()

        self.udp_socket.bound_socket.close()

        while not result_q.empty():
            message_received, address = result_q.get()
            self.assertEqual(message_received, b'Im responding!')
            self.assertEqual(address, ('127.0.0.1', 5001))




if __name__ == "__main__":
    unittest.main()
