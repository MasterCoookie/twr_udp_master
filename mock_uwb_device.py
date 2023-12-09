import socket
import sys
import time

from helper_functions import *

from threading import Thread, Event
from random import randint

moving = 0

tag_addresses = ['FF', 'GG', 'HH', 'II', 'JJ', 'KK', 'LL', 'MM', 'NN', 'OO', 'PP']

distances_dict_a = {
    "AA": 4.12, #3, 4, 5
    "BB": 5.91, #2, 2, 2
    "CC": 4.47, #3, 3, 3
    "DD": 8.6, #0, 0, 1
    "EE": 8.86, #0, 0, .5
}

distances_dict_b = {
    "AA": 4.74, #3, 4, 5
    "BB": 1.87, #2, 2, 2
    "CC": 3.24, #3, 3, 3
    "DD": 1.87, #0, 0, 1
    "EE": 2.29, #0, 0, .5
}

distances_array = [
    {"AA": 10.68, "BB": 8.72, "CC": 9.95, "DD": 6.4, "EE": 6.65}, # -4, -4, 4
    {"AA": 9.27, "BB": 7.35, "CC": 8.54, "DD": 5.2, "EE": 5.5}, # -3, -3, 4
    {"AA": 7.87, "BB": 6, "CC": 7.14, "DD": 4.12, "EE": 4.5}, # -2, -2, 4
    {"AA": 6.48, "BB": 4.69, "CC": 5.74, "DD": 3.32, "EE": 3.77}, # -1, -1, 4
    {"AA": 5.1, "BB": 3.46, "CC": 4.36, "DD": 3, "EE": 3.5}, # 0, 0, 4
    {"AA": 3.74, "BB": 2.45, "CC": 3, "DD": 3.32, "EE": 3.77}, # 1, 1, 4
    {"AA": 2.5, "BB": 2, "CC": 1.73, "DD": 4.12, "EE": 4.5}, # 2, 2, 4
    {"AA": 1.41, "BB": 2.45, "CC": 1, "DD": 5.2, "EE": 5.5}, # 3, 3, 4
    {"AA": 1.41, "BB": 3.46, "CC": 1.73, "DD": 6.4, "EE": 6.65}, # 4, 4, 4
]

SWITCH = 24

def uwb_mock(num, ended, verbose=False, tag_address=None):
    receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_socket.bind((f'127.0.0.{num}', 5000 + num))
    receiver_socket.settimeout(.5)
    distances_dict = distances_dict_a

    count = 0
    index = 0
    while not ended.is_set():
        if moving == 1 and count == SWITCH:
            print("Switching to position b")
            distances_dict = distances_dict_b
        elif moving == 1 and count == SWITCH * 2:
            print("Switching to position a")
            distances_dict = distances_dict_a
            count = 0
        elif moving == 2:
            if count > 4:
                index += 1
                count = 0
            if index >= len(distances_array):
                index = 0
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

            if moving == 1:
                rand_distance_full = distances_dict[message_decoded]
            elif moving == 2:
                print("index", index)
                rand_distance_full = distances_array[index][message_decoded]
            else:
                rand_distance_1 = randint(0, 100)
                rand_distance_2 = randint(0, 100)
                rand_distance_full = str(rand_distance_1) + "." + str(rand_distance_2)

            time.sleep(randint(0, 50) / 1000)

            msg = f'DIST {tag_address} to {message_decoded}: {rand_distance_full}m'
            print(msg)

            receiver_socket.sendto(msg.encode(), address)
            count += 1
        except socket.timeout:
            if verbose:
                print(f"Mock 127.0.0.{num}:{5000+num} Receiver socket timeout!")

    receiver_socket.close()

if __name__ == "__main__":
    count = int(sys.argv[1])
    moving = int(sys.argv[2] if len(sys.argv) > 2 else 0)

    if moving == 1:
        print("Repositioning tag")

    if moving == 2:
        print("Moving tag")

    ended = Event()
    ended.clear()

    threads = []
    for i in range(count):
        threads.append(Thread(target=uwb_mock, args=(i + 1, ended, True, tag_addresses[i],)))
        threads[-1].start()

    input("Starting... Press any button to end...\n")
    
    time.sleep(1)

    ended.set()
    for thread in threads:
        thread.join()
