from random import randint

from queuing_stategy import QueuingStrategy

class CompleteRandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        for tag in tags_dict.values():
            anchor = tag.available_devices.pop(randint(0, len(tag.available_devices) - 1))
            self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))

