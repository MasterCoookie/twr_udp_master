import socket

class UDPSocket:
    def __init__(self, out_port, devices_count, timeout=.5):
        self.out_port = out_port
        self.devices_count = devices_count

        self.bound_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bound_socket.bind(('0.0.0.0', out_port))
        self.bound_socket.settimeout(timeout)

    def send(self, message_encoded, ip, taget_port, verbose=False):
        if verbose:
            print(f"Sending message: {message_encoded.decode()} to {ip}:{taget_port}")
        self.bound_socket.sendto(message_encoded, (ip, taget_port))

    def receive(self, verbose=False):
        try:
            message_encoded, address = self.bound_socket.recvfrom(1024)
            if verbose:
                print(f"Received message: {message_encoded.decode()} from {address}")
            return message_encoded, address
        except socket.timeout:
            if verbose:
                print("Socket timeout")
            return None, None
