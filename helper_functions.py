import socket

def receiver_process(ended, verbose=False):
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(('127.0.0.1', 5001))
    receiver_socket.settimeout(.5)

    while not ended.is_set():
        try:
            message_received, address = receiver_socket.recvfrom(1024)
            if verbose:
                print(f"Helper has received message: {message_received.decode()} from {address}")

            receiver_socket.sendto(b'Im responding!', address)
        except socket.timeout:
            if verbose:
                print("Helpers: Receiver socket timeout!")

    receiver_socket.close()