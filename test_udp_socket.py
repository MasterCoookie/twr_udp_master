import unittest
import socket
from udp_socket import UDPSocket

class TestUDPSocket(unittest.TestCase):
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
        

if __name__ == '__main__':
    unittest.main()