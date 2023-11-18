import numpy as np

from queuing_stategy import QueuingStrategy

from positioning_functions import trilaterate_3d_4dists

class ClosestStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        for tag in tags_dict.values():
            if tag.distances_available >= 4:
                trilateration_list = []
                available_copy = tag.available_devices.copy()
                while len(trilateration_list) < 4:
                    anchor = available_copy.pop(0)
                    if anchor.distance is not None:
                        trilateration_list.append(anchor.position)

                # print("trilateration_list ", trilateration_list)
                tag_position = trilaterate_3d_4dists(trilateration_list)

                print("tag_position ", tag_position)

                i = 0
                while i < len(tag.available_devices):
                    tag.available_devices[i].distance = np.linalg.norm(np.array(tag.available_devices[i].position[:3]) - tag_position)
                    print(f"anchor {tag.available_devices[i].uwb_address} {tag.available_devices[i].distance}")
                    i += 1

                tag.available_devices.sort(key=lambda x: x.distance if x.distance is not None else 1000)
                for anchor in tag.available_devices:
                    print("Sorted:", anchor.uwb_address, anchor.distance)

                for i in range(4):
                    print("Putting:", tag.available_devices[i].uwb_address, tag.ip, tag.device_port)
                    self.prepared_queue.put((tag.available_devices[i].uwb_address.encode(), tag.ip, tag.device_port))

                tag.distances_available = 0
            else:
                for anchor in tag.available_devices:
                    self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))

    def decode_message(self, message_encoded, tags_dict):
        msg = message_encoded[1]
        if msg is None:
            return (message_encoded[0], None)
        message_decoded = message_encoded[1].decode('utf-8')

        uwb_addr = message_decoded.split(" ")[1].split(":")[0]
        distance = float(message_decoded.split(" ")[2].split("m")[0])

        for tag in tags_dict.values():
            for anchor in tag.available_devices:
                if anchor.uwb_address == uwb_addr:
                    anchor.distance = distance
                    if tag.distances_available < len(tag.available_devices):
                        tag.distances_available += 1
                    break
            
            tag.available_devices.sort(key=lambda x: x.distance if x.distance is not None else 1000)


        return (message_encoded[0], message_decoded)
