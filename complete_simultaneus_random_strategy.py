from random import randint

from queuing_stategy import QueuingStrategy

class CompleteSimultaneusRandomStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        pass

    def decode_message(self, message_encoded, tags_dict):
        pass
