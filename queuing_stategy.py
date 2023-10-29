from abc import ABC, abstractmethod
from queue import Queue

class QueuingStartegy(ABC):
    def __init__(self) -> None:
        self.prepared_queue = Queue()
    
    @abstractmethod
    def prepare_queue(self, tags_list):
        pass