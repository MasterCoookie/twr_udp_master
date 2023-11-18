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
        
        self.prepared_queue.put(("dupa", "dupa", "dupa"))

    def decode_message(self, message_encoded, tags_dict):
        pass
