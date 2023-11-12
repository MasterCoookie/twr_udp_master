from abc import ABC, abstractmethod
from multiprocessing import Queue

class QueuingStrategy(ABC):
    def __init__(self) -> None:
        self.prepared_queue = Queue()
    
    @abstractmethod
    def prepare_queue(self, tags_dict):
        pass

    @abstractmethod
    def decode_message(self, message_encoded, tags_dict):
        pass