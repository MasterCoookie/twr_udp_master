from abc import ABC, abstractmethod
from multiprocessing import Queue

class QueuingStrategy(ABC):
    def __init__(self) -> None:
        self.prepared_queue = Queue()
    
    @abstractmethod
    def prepare_queue(self, tags_list):
        pass