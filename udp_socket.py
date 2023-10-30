import socket
import time
from multiprocessing import Queue

class UDPSocket:
    '''
    Single socket for sending and receiving UDP messages.
    Only one instance of it should be created in the program.
    The socket is designed to work in multithreaded environment.
    '''
    def __init__(self, out_port, devices_count, timeout=.5, post_send_delay=0.01):
        self.out_port = out_port
        self.devices_count = devices_count

        self.bound_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bound_socket.bind(('0.0.0.0', out_port))
        self.bound_socket.settimeout(timeout)

        self.msg_queue = Queue()
        self.received_queue = Queue()
        self.post_send_delay = post_send_delay

    def send(self, message_encoded, ip, taget_port, verbose=False):
        '''
        Sneds a pre-encoded message to the specified ip and port.
        message_encoded - bytes
        ip - string
        target_port - int
        '''
        if verbose:
            print(f"Sending message: {message_encoded.decode()} to {ip}:{taget_port}")
        self.bound_socket.sendto(message_encoded, (ip, taget_port))

    def receive(self, verbose=False):
        '''
        Receives a message from the socket.
        Returns the encoded message and the address of the sender.
        If the socket times out, returns None, None.
        '''
        try:
            message_encoded, address = self.bound_socket.recvfrom(1024)
            if verbose:
                print(f"Received message: {message_encoded.decode()} from {address}")
            return message_encoded, address
        except socket.timeout:
            if verbose:
                print("Socket timeout")
            return None, None

    def sending_process(self, ended):
        '''
        Sends messages from the queue in an infinite loop.
        Ment to be run in a separate thread.
        '''
        while not ended.is_set():
            if self.msg_queue.empty():
                time.sleep(.1)
                print("Queue empty!")
                continue
            else:
                message_encoded, ip, target_port = self.msg_queue.get()
                self.send(message_encoded, ip, target_port)

                response_encoded, response_address = self.receive()

                self.received_queue.put((response_encoded, response_address))

                time.sleep(self.post_send_delay)
