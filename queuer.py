from multiprocessing import Queue

from uwb_tag import UWBTag
from uwb_device import UWBDevice

class Queuer:
    def __init__(self, queuing_strategy, queue_lower_limit=3, queue_upper_limit=5):
        # self.tags_dict = tags_dict
        self.queue_lower_limit = queue_lower_limit
        self.queue_upper_limit = queue_upper_limit
        self.prepared_queue = Queue()

        self.queuing_strategy = queuing_strategy

    def fill_queue(self, queue):
        if queue.empty():
            while queue.qsize() < self.queue_upper_limit:
                if(not self.prepared_queue.empty()):
                    queue.put(self.prepared_queue.get())
                else:
                    if queue.qsize() > self.queue_lower_limit:
                        break
                    else:
                        raise Exception("Prepared queue is empty")
            self.prepared_queue = Queue()

        return queue

    def encode_queue(self, tags_dict):
        while self.prepared_queue.qsize() < self.queue_upper_limit:
            self.queuing_strategy.prepare_queue(tags_dict)
            #TODO - potentially rework this
            print("Encode available size", tags_dict['FF'].distances_available)
            while not self.queuing_strategy.prepared_queue.empty():
                self.prepared_queue.put(self.queuing_strategy.prepared_queue.get())
                # print("Putting in prepared queue:", self)
            # self.prepared_queue = self.queuing_strategy.prepared_queue

    def queing_process(self, ended, message_queue, tags_dict):
        while not ended.is_set():
            self.encode_queue(tags_dict)
            self.fill_queue(message_queue)

    def results_decode(self, encoded_queue, decoded_queue, tags_dict):
        while not encoded_queue.empty():
            print("Decode available size", tags_dict['FF'].distances_available)
            message_decoded = self.queuing_strategy.decode_message(encoded_queue.get(), tags_dict)

            decoded_queue.put((message_decoded[0], message_decoded[1]))

    def generate_dict(self, ui_passed_dict):
        generated_dict = {}
        for key, value in ui_passed_dict.items():
            tag_available_devices = [UWBDevice(None, None, device_addr, x, y, z) for device_addr, x, y, z in value[2]]
            for anchor in tag_available_devices:
                print("anchor", anchor.uwb_address, anchor.position)
            tag = UWBTag(ip=value[0], uwb_address=key, device_port=value[1], available_devices=tag_available_devices)
            generated_dict[key] = tag
        
        return generated_dict    
