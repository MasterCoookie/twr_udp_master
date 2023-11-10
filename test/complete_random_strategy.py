from random import randint

from queuing_stategy import QueuingStrategy

class CompleteRandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        tags_queues = []
        for index, tag in enumerate(tags_dict.values()):
            available_copy = tag.available_devices.copy()
            while len(available_copy) > 0:
                anchor = available_copy.pop(randint(0, len(available_copy) - 1))

            self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))

