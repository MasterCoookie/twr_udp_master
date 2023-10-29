from random import choice
from queuing_stategy import QueuingStrategy

class RandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_list):
        for tag in tags_list:
            self.prepared_queue.put((tag, choice(tag.available_devices)))