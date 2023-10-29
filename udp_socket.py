import socket

class UDPSocket:
    def __init__(self, out_port, devices_count):
        self.out_port = out_port
        self.devices_count = devices_count

        self.bound_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bound_socket.bind(('0.0.0.0', out_port))