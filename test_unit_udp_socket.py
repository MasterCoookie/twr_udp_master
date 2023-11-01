import unittest
import socket
from udp_socket import UDPSocket
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

    def receiver_process(self, ended):
        receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        receiver_socket.bind((self.ip, self.port + 1))
        receiver_socket.settimeout(.5)

        while not ended.is_set():
            try:
                message_received, address = receiver_socket.recvfrom(1024)
                self.assertAlmostEqual(message_received, b'Hello World!')
                self.assertEqual((self.ip, self.port), address)

                receiver_socket.sendto(b'Im responding!', address)
            except socket.timeout:
                self.fail("Socket timeout")
        

    def test_sending_process(self):
        udp_socket = UDPSocket(self.port, self.devices_count)
        msg_queue = Queue((b'Hello World!', self.ip, self.port + 1), (b'Hello World2', self.ip, self.port + 1))
        res_queue = Queue()

        ended = Event()
        ended.clear()

        p1 = Process(target=self.receiver_process, args=(ended))
        p2 = Process(target=udp_socket.sending_process, args=(ended, msg_queue, res_queue))

        p1.start()
        p2.start()

        time.sleep(.25)


if __name__ == '__main__':
    unittest.main()