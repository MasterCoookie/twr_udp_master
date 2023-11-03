from multiprocessing import Queue

class Queuer:
    def __init__(self, tags_dict, queuing_strategy, queue_lower_limit=3, queue_upper_limit=5):
        self.tags_dict = tags_dict
        self.queue_lower_limit = queue_lower_limit
        self.queue_upper_limit = queue_upper_limit
        self.prepared_queue = Queue()

        self.queuing_strategy = queuing_strategy

    def fill_queue(self, queue):
        if queue.qsize() < self.queue_lower_limit:
            while queue.qsize() < self.queue_upper_limit:
                if(not self.prepared_queue.empty()):
                    queue.put(self.prepared_queue.get())
                else:
                    if queue.qsize() > self.queue_lower_limit:
                        break
                    else:
                        raise Exception("Queue is empty")

        return queue

    def encode_queue(self):
        while self.prepared_queue.qsize() < self.queue_lower_limit:
            self.queuing_strategy.prepare_queue(self.tags_dict)
            #TODO - potentially rework this
            self.prepared_queue = self.queuing_strategy.prepared_queue

    def queing_process(self, ended, message_queue):
        while not ended.is_set():
            self.encode_queue()
            self.fill_queue(message_queue)

    def results_decode(self, message_encoded):
        pass
    
    
