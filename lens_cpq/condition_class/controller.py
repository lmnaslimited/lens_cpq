from lens_cpq.condition_class.interface import Ifcontroller
from typing import List, Union
from abc import abstractmethod

class Controller(Ifcontroller):
    controllers: List[Ifcontroller]
    viewcontroller: List[Ifcontroller]
    modelcontrller: List[Ifcontroller]
    doctype: str
    event: str
    event_fields: Union[list, str]

    # this controller class start a circular dependencey becuase
    # this call view and model and in view that call controller again and same goes for model
    # so i put the import on constructor

    def __init__(self, doctype: str, event: str, events: Union[list, str]):
        from lens_cpq.condition_class.view_controller import ClViewController
        from lens_cpq.condition_class.model_controller import ClModelController
        self.doctype = doctype
        self.event = event
        self.event_fields = events
        self.viewcontroller =  ClViewController(doctype, event, events)
        self.modelcontroller = ClModelController(doctype, event, events)

    # @abstractmethod
    # TypeError: Can't instantiate abstract class Controller with abstract method execute
    # Possible source of error: lens_cpq (app)
    def execute(self):
        if self.viewcontroller.is_sate_changed():
            print("[Controller] State changed detected, calling ModelController")
            self.modelcontroller.execute()
        else:
            print("[Controller] No state change, skipping ModelController")
