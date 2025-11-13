from lens_cpq.condition_class.controller import Controller

class ClViewController(Controller):
    def __init__(self, doctype, event, events):
        # super().__init__(doctype, event, events) 
        # calling the super creating a circular dependency
        self.doctype = doctype
        self.event = event
        self.events = events
    
    def is_sate_changed(self)->bool:
        print("[ViewController] Checking if state changed...")
        return True

    def execute(self):
        print("[ViewController] Executing view logic")