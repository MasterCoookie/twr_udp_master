import time

from random import choice
from queuing_stategy import QueuingStrategy

class RandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        for tag in tags_dict.values():
            anchor = choice(tag.available_devices)
            self.prepared_queue.put((anchor.uwb_address.encode(), tag.ip, tag.device_port))
            time.sleep(.005)

    def results_decode(self, message_encoded):
        pass
