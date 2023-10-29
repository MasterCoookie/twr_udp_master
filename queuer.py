from queue import Queue
from random import choice

class Queuer:
    def __init__(self, tags_list, queue_lower_limit=3, queue_upper_limit=5):
        self.tags_list = tags_list
        self.queue_lower_limit = queue_lower_limit
        self.prepared_queue = Queue()

    def fill_queue(self, queue):
        if len(queue) < self.queue_lower_limit:
            while len(queue) < self.queue_upper_limit:
                queue.put(self.prepared_queue.get())
        return queue
    
    def prepare_queue(self):
        pass