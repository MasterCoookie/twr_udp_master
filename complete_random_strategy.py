from random import randint

from queuing_stategy import QueuingStrategy

class CompleteRandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        tags_queues = [[] for _ in range(len(tags_dict))]
        total_count = 0
        for index, tag in enumerate(tags_dict.values()):
            available_copy = tag.available_devices.copy()
            while len(available_copy) > 0:
                anchor = available_copy.pop(randint(0, len(available_copy) - 1))
                tags_queues[index].append((tag, anchor))
                total_count += 1
        
        for _ in range(total_count):
            i = 0
            while i < len(tags_queues):
                if len(tags_queues[i]) > 0:
                    tag, anchor = tags_queues[i].pop(0)
                    self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))
                i += 1
