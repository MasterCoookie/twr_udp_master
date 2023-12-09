from random import randint

from queuing_stategy import QueuingStrategy

class CompleteSimultaneusRandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        tags_queues = [[] for _ in range(len(tags_dict))]
        total_count = 0

    def decode_message(self, message_encoded, tags_dict):
        msg = message_encoded[1]
        if msg is None:
            return (message_encoded[0], None)
        message_decoded = message_encoded[1].decode('utf-8')
        return (message_encoded[0], message_decoded)
