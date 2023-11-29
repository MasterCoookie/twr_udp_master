import socket
import sys
import time

from helper_functions import *

from threading import Thread, Event
from random import randint

moving = False

distances_dict_a = {
    "AA": 4.12,
    "BB": 5.91,
    "CC": 4.47,
    "DD": 8.6,
    "EE": 4.12,
}

distances_dict_b = {
    "AA": 6.1,
    "BB": 2.87,
    "CC": 4.5,
    "DD": 0.5,
    "EE": 1,
}

def uwb_mock(num, ended, verbose=False):
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind((f'127.0.0.{num}', 5000 + num))
    receiver_socket.settimeout(.5)
    distances_dict = distances_dict_a

    count = 0
    while not ended.is_set():
        if moving and count == 12:
            print("Switching to position b")
            distances_dict = distances_dict_b
        elif moving and count == 24:
            print("Switching to position a")
            distances_dict = distances_dict_a
            count = 0
        try:
            message_received, address = receiver_socket.recvfrom(1024)
            message_decoded = message_received.decode('utf-8')
            if verbose:
                print(f"Mock nr {num} has received message: {message_decoded} from {address}")

            random_result  = randint(0, 10)

            if not moving:
                if random_result == 0:
                    receiver_socket.sendto(b'ERR', address)
                    continue
                    
                if random_result < 3:
                    continue

            if moving:
                rand_distance_full = distances_dict[message_decoded]
            else:
                rand_distance_1 = randint(0, 100)
                rand_distance_2 = randint(0, 100)
                rand_distance_full = str(rand_distance_1) + "." + str(rand_distance_2) + "m\n"

            time.sleep(randint(0, 50) / 1000)

            receiver_socket.sendto(f'DIST FF to {message_decoded}: {rand_distance_full}m'.encode(), address)
            count += 1
        except socket.timeout:
            if verbose:
                print(f"Mock 127.0.0.{num}: Receiver socket timeout!")

    receiver_socket.close()

if __name__ == "__main__":
    count = int(sys.argv[1])
    moving = bool(sys.argv[2] if len(sys.argv) > 2 else False)

    if moving:
        print("Moving anchors")

    ended = Event()
    ended.clear()

    threads = []
    for i in range(count):
        threads.append(Thread(target=uwb_mock, args=(i + 1, ended, True)))
        threads[-1].start()

    input("Starting... Mash enter to end...\n")
    
    time.sleep(1)

    ended.set()
    for thread in threads:
        thread.join()
