import socket

def receiver_process(ended):
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind(('127.0.0.1', 5001))
    receiver_socket.settimeout(.5)

    while not ended.is_set():
        try:
            message_received, address = receiver_socket.recvfrom(1024)
            print(f"Received message: {message_received.decode()} from {address}")

            receiver_socket.sendto(b'Im responding!', address)
        except socket.timeout:
            print("Helpers: Receiver socket timeout!")

    receiver_socket.close()