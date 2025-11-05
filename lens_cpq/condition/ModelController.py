from lens_cpq.condition.inBaseController import BaseController

class ModelController(BaseController):
    def __init__(self, doctype=None, on_field=None):
        super().__init__(doctype, on_field)

    def get(self):
        #get the condition type's input sequence
        #get the condition value
        pass

    def set(self):
        pass

    def execute(self):
        # self.get()
        pass