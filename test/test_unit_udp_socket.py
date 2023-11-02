import unittest
import socket
import time

from udp_socket import UDPSocket
from helper_functions import receiver_process

from multiprocessing import Queue, Process, Event

class TestUDPSocket(unittest.TestCase):
    #TODO - teardown
    def setUp(self):
        self.ip = '127.0.0.1'
        self.port = 5000
        self.devices_count = 1
    
    def test_send_receive_yourself(self):
        udp_socket = UDPSocket(self.port, self.devices_count)
        message = b'Hello World!'
        udp_socket.send(message, self.ip, self.port)
        message_received, address = udp_socket.receive()
        self.assertEqual(message, message_received)
        self.assertEqual((self.ip, self.port), address)
        udp_socket.bound_socket.close()

    def test_send_other(self):
        udp_socket = UDPSocket(self.port, self.devices_count)
        message = b'Hello World!'

        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver_socket.bind((self.ip, 5001))

        udp_socket.send(message, self.ip, 5001)
        message_received, address = receiver_socket.recvfrom(1024)
        self.assertEqual(message, message_received)
        self.assertEqual((self.ip, self.port), address)

        receiver_socket.close()
        udp_socket.bound_socket.close()

    def test_receive_timeout(self):
        udp_socket = UDPSocket(self.port, self.devices_count, timeout=.1)
        message_received, address = udp_socket.receive()
        self.assertIsNone(message_received)
        self.assertIsNone(address)
        udp_socket.bound_socket.close()
        

    def test_sending_process(self):
        udp_socket = UDPSocket(self.port, self.devices_count)
        msg_queue = Queue()
        res_queue = Queue()

        msg_queue.put((b'Hello World!', self.ip, self.port + 1))
        msg_queue.put((b'Hello World2', self.ip, self.port + 1))


        ended = Event()
        ended.clear()

        p1 = Process(target=receiver_process, args=(ended, ))
        p2 = Process(target=udp_socket.sending_process, args=(ended, msg_queue, res_queue))

        p1.start()
        p2.start()

        time.sleep(.005)
        msg_queue.put((b'Hello World3', self.ip, self.port + 1))
        time.sleep(.005)
        msg_queue.put((b'Hello World4', self.ip, self.port + 1))
       
        time.sleep(.15)

        ended.set()
        udp_socket.bound_socket.close()

        p1.join()
        p2.join()

        self.assertEqual(res_queue.qsize(), 4)
        q_element = res_queue.get()
        self.assertEqual(q_element[0], b'Im responding!')
        self.assertEqual(q_element[1], (self.ip, self.port + 1))


if __name__ == '__main__':
    unittest.main()