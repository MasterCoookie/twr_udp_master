import time

import numpy as np

from queuing_stategy import QueuingStrategy

from positioning_functions import trilaterate_3d_4dists, polyfit_3d

class ClosestStrategy(QueuingStrategy):
    def __init__(self, regression_treshold=0):
        super().__init__()
        self.regression_treshold = regression_treshold
        if regression_treshold:
            self.points_dict = {}
            self.start_time = time.time()

    def get_passed_time(self):
        return time.time() - self.start_time

    def prepare_queue(self, tags_dict):
        for tag in tags_dict.values():
            print('Closest distances available', tag.distances_available)
            if tag.distances_available >= 4:
                trilateration_list = []
                tag.available_devices.sort(key=lambda x: x.distance if x.distance is not None else 1000)
                available_copy = tag.available_devices.copy()
                print("available_copy len", len(available_copy))

                while len(trilateration_list) < 4:
                    anchor = available_copy.pop(0)
                    print("anchor", anchor.uwb_address, anchor.distance)
                    if anchor.distance is not None:
                        trilateration_list.append(anchor.position)

                print("trilateration_list ", trilateration_list)
                res = trilaterate_3d_4dists(trilateration_list)
                tag_position = list(res) if res is not None else None

                if tag_position is None:
                    tag.distances_available = 0
                    for anchor in tag.available_devices:
                        anchor.distance = None
                    tags_dict[tag.uwb_address] = tag
                    print("is none")
                    # for anchor in tag.available_devices:
                    #     self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))
                    continue

                print("tag_position ", tag_position)

                if self.regression_treshold:
                    tag_position.append(self.get_passed_time())
                    if tag.uwb_address in self.points_dict:
                        self.points_dict[tag.uwb_address].insert(0, tag_position)
                    else:
                        self.points_dict[tag.uwb_address] = [tag_position]

                    if len(self.points_dict[tag.uwb_address]) > self.regression_treshold:
                        tag_position = list(polyfit_3d(self.points_dict[tag.uwb_address][0:self.regression_treshold]))

                    while len(self.points_dict[tag.uwb_address]) > 99:
                        self.points_dict[tag.uwb_address] = self.points_dict[tag.uwb_address][:99]


                i = 0
                while i < len(tag.available_devices):
                    tag.available_devices[i].distance = np.linalg.norm(np.array(tag.available_devices[i].position[:3]) - tag_position[:3])
                    print(f"anchor {tag.available_devices[i].uwb_address} {tag.available_devices[i].distance}")
                    i += 1

                tag.available_devices.sort(key=lambda x: x.distance if x.distance is not None else 1000)
                for anchor in tag.available_devices:
                    print("Sorted:", anchor.uwb_address, anchor.distance)

                for i in range(4):
                    print("Putting:", tag.available_devices[i].uwb_address, tag.ip, tag.device_port)
                    self.prepared_queue.put((tag.available_devices[i].uwb_address.encode(), tag.ip, tag.device_port))

                # tag.distances_available = 0
            else:
                print("Scanning")
                for anchor in tag.available_devices:
                    anchor.distance = None
                    self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))

    def decode_message(self, message_encoded, tags_dict):
        msg = message_encoded[1]
        if msg is None:
            return (message_encoded[0], None)
        message_decoded = message_encoded[1].decode('utf-8')

        if message_decoded.startswith("ERR"):
            return (message_encoded[0], message_decoded)
        
        # print("split:", message_decoded.split(" ")[3])

        anchor_uwb_addr = message_decoded.split(" ")[3].split(":")[0]
        distance = float(message_decoded.split(" ")[4].split("m")[0])

        for tag in tags_dict.copy().values():
            for anchor in tag.available_devices:
                if anchor.uwb_address == anchor_uwb_addr:
                    anchor.distance = distance
                    # if tag.distances_available < len(tag.available_devices):
                    #     print("Incrementing")
                    #     tag.distances_available += 1
                    tag.distances_available = 0
                    for anchor in tag.available_devices:
                        if anchor.distance is not None:
                            tag.distances_available += 1
                    break
            
            tag.available_devices.sort(key=lambda x: x.distance if x.distance is not None else 1000)

            # print('available_for given', tags_dict[tag.uwb_address])
            tags_dict[tag.uwb_address] = tag

        return (message_encoded[0], message_decoded)
