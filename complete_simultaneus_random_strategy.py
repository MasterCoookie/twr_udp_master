from random import randint
from collections import deque

from queuing_stategy import QueuingStrategy

class CompleteSimultaneusRandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()


    def prepare_queue(self, tags_dict):
        tags_queues = []
        total_count = 0
        for index, tag in enumerate(tags_dict.values()):
            available_copy = deque(tag.available_devices.copy())
            available_copy.rotate(-index)
            tags_queues.append(available_copy)
            total_count += len(available_copy)

        tags_list = list(tags_dict.values())

        while total_count > 0:
            i = 0
            while i < len(tags_queues):
                if len(tags_queues[i]) > 0:
                    anchor = tags_queues[i].popleft()
                    self.prepared_queue.put((anchor.uwb_address.encode(), tags_list[i].ip, tags_list[i].device_port))
                    total_count -= 1
                i += 1
            
            

    def decode_message(self, message_encoded, tags_dict):
        msg = message_encoded[1]
        if msg is None:
            return (message_encoded[0], None)
        message_decoded = message_encoded[1].decode('utf-8')
        if message_decoded.startswith("ERR"):
            return (message_encoded[0], message_decoded)
        return (message_encoded[0], message_decoded)
