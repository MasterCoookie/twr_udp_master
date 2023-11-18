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

                print("trilateration_list ", trilateration_list)
                tag_position = trilaterate_3d_4dists(trilateration_list)

                print("tag_position ", tag_position)

                for anchor in tag.available_devices:
                    anchor.distance = np.linalg.norm(np.array(anchor.position[:3]) - tag_position)
                    print(f"anchor {anchor.uwb_address} {anchor.distance}")

                tag.available_devices.sort(key=lambda x: x.distance)

                for i in range(4):
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
                    tag.distances_available += 1
                    break


        return (message_encoded[0], message_decoded)
