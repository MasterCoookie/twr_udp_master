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

        for index, tag in enumerate(tags_dict.values()):
            for _ in range(len(tags_queues[index])):
                anchor = tags_queues[index].popleft()
                self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))
            
            

    def decode_message(self, message_encoded, tags_dict):
        msg = message_encoded[1]
        if msg is None:
            return (message_encoded[0], None)
        message_decoded = message_encoded[1].decode('utf-8')
        if message_decoded.startswith("ERR"):
            return (message_encoded[0], message_decoded)
        return (message_encoded[0], message_decoded)
