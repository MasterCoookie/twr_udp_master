from queuing_stategy import QueuingStrategy

class ClosestStrategy(QueuingStrategy):
    def __init__(self):
        super().__init__()

    def prepare_queue(self, tags_dict):
        pass

    def decode_message(self, message_encoded, tags_dict):
        pass
