from lens_cpq.condition_class.controller import Controller
from lens_cpq.condition_class.interface import IfCondtions
from lens_cpq.condition_class.input_condition_factory import InputFieldConditionFactory
from typing import List

class ClModelController(Controller):
    conditions: List[IfCondtions]
    def __init__(self, doctype, event, events):
        # super().__init__(doctype, event, events)
        # calling the super creating a circular dependency
        self.doctype = doctype
        self.event = event
        self.events = events
    
    def execute(self):
        print("[ModelController] Executing model logic...")

        # 
        # dummy record to simulate the condition value's input value
        records = [
            {"field_evalutionType": "constant"},
            {"field_evalutionType": "api"},
            {"field_evalutionType": "formula"},
        ]

        for record in records:
            condition = InputFieldConditionFactory.create("Quotation", "discount", 10, record)
            print(f"[ModelController] Created condition of type: {record['field_evalutionType']}")
            condition.evaluate()
        # 