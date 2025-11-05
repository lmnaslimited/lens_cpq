from abc import ABC, abstractmethod

class BaseController(ABC):
    def __init__(self, doctype=None, on_field=None):
        self.doctype = doctype
        self.on_field = on_field

    @abstractmethod
    def get(self):
        pass

    @abstractmethod
    def set(self):
        pass

    @abstractmethod
    def execute(self):
        pass