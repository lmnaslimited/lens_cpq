from lens_cpq.condition_class.interface import Ifcontroller
from typing import List, Union
from abc import abstractmethod
# from lens_cpq.condition_class.view_controller import ClViewController
# from lens_cpq.condition_class.model_controller import ClModelController

class Controller(Ifcontroller):
    view_controller: Ifcontroller
    model_controller: Ifcontroller
    doctype: str
    event: str
    event_fields: Union[list, str]

    # this controller class start a circular dependencey becuase
    # this call view and model here and in view class it call controller again and same goes for model
    #
    # Failed to get method for command lens_cpq.condition_class.entry_point.start_condition with cannot 
    # import name 'Controller' from partially initialized module 'lens_cpq.condition_class.controller' 
    # (most likely due to a circular import) (/workspace/frappe-bench/apps/lens_cpq/lens_cpq/condition_class/controller.py)

    #  so i put the import on constructor
    def __init__(self, doctype: str, event: str, events: Union[list, str]):
        # commented on Day 2 review
        # from lens_cpq.condition_class.view_controller import ClViewController
        # from lens_cpq.condition_class.model_controller import ClModelController
        self.doctype = doctype
        self.event = event
        self.event_fields = events
        # commented on Day 2 review
        # self.view_controller =  ClViewController(doctype, event, events)
        # self.model_controller = ClModelController(doctype, event, events)

    # @abstractmethod
    # TypeError: Can't instantiate abstract class Controller with abstract method execute
    # Possible source of error: lens_cpq (app)

# second review (day 2)
# put public method, --> init two controller, 
    def init_controller(self):
        from lens_cpq.condition_class.view_controller import ClViewController
        from lens_cpq.condition_class.model_controller import ClModelController

        self.view_controller =  ClViewController(self.doctype, self.event, self.event_fields)
        self.model_controller = ClModelController(self.doctype, self.event, self.event_fields)

    def execute(self):
        print(f"[Controller] State changed detected, calling ModelController,  : {self.doctype}")
        if self.view_controller.is_sate_changed():
            print("[Controller] State changed detected, calling ModelController")
            # self.model_controller.execute()
        else:
            print("[Controller] No state change, skipping ModelController")
