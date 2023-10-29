from queue import Queue

class Queuer:
    def __init__(self, tags_list, queuing_strategy, queue_lower_limit=3, queue_upper_limit=5):
        self.tags_list = tags_list
        self.queue_lower_limit = queue_lower_limit
        self.queue_upper_limit = queue_upper_limit
        self.prepared_queue = Queue()

        self.queuing_strategy = queuing_strategy

    def fill_queue(self, queue):
        #TODO - fix bug with len
        if len(queue) < self.queue_lower_limit:
            while len(queue) < self.queue_upper_limit:
                queue.put(self.prepared_queue.get())
        return queue
    
    def prepare_queue(self):
        if len(self.prepared_queue) < self.queue_lower_limit:
            self.queuing_strategy.prepare_queue(self.tags_list)
