from lens_cpq.condition_class.controller import Controller

class ClViewController(Controller):
    # commented out on review 2
    # def __init__(self, doctype, event, events):
    #     # super().__init__(doctype, event, events) 
    #     # calling the super creating a circular dependency
    #     self.doctype = doctype
    #     self.event = event
    #     self.events = events
    
    # this function is for checking if field was changed by user or condition type 
    # (final / need to trigger another condition sequence)
    def is_sate_changed(self)->bool:
        # Print statements were added for testing
        # to verify whether the implemented class
        # has access to the doctype passed
        print(f"[ViewController] Checking if state changed...: {self.doctype}")
        return True

    def execute(self):
        print("[ViewController] Executing view logic")