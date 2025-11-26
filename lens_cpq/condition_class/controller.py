from lens_cpq.condition_class.condition import ClCondtions
from lens_cpq.condition_class.interface import Ifcontroller
from typing import List, Union, Dict
from lens_cpq.condition_class.interface import IfCondtions

class Controller(Ifcontroller):

    view_controller: Ifcontroller
    model_controller: Ifcontroller
    doctype: str
    event: str
    fields: Union[list, str]

    def __init__(self, doctype: str, event: str, fields: Union[list, str]):
        self.doctype = doctype
        self.event = event
        self.fields = fields
    
    def set_model_and_view(self, view_instance, model_instance):
        self.view_controller = view_instance
        self.model_controller = model_instance


    def execute(self):
        print(f"[Controller] Field changed: {self.fields}")
        condition = ClCondtions(self.doctype, self.event, self.fields)
        condition.attach_model(self.view_controller,self.model_controller) #to avoid round import we injecting the model

        affected_conditions = condition.resolve_condition_chain(
            self.fields, self.event
        )

        condition.execute_conditions(affected_conditions)

    
class ClViewController(Controller):

   
    def __init__(self, doctype, event, events):
        super().__init__(doctype, event, events) 
        
    def is_sate_changed(self)->bool:
        return True
    
    def is_value_present_in_doc(self, input_field_names:List)->bool:
        return True

    def execute(self):
        print("[ViewController] Executing view logic")
    
    def set_model_and_view(self, view_instance, model_instance):
        self.view_controller = view_instance
        self.model_controller = model_instance
        

class ClModelController(Controller):
    conditions: List[IfCondtions]
    
    def __init__(self, doctype, event, events):
        super().__init__(doctype, event, events)
        
    def execute(self):
        print("[ModelController] Executing model logic...")
    
    def set_model_and_view(self, view_instance, model_instance):
        self.view_controller = view_instance
        self.model_controller = model_instance

    # STEP 1: Fetch INPUT SEQUENCE records
    def fetch_input_sequence(self, field_name: str) -> List[Dict]:
        print(f"[Model] Fetching Input Sequence for: {field_name}")
        if field_name == "x_output":
            return [
                {"name": "INP-0002", "field_name": "2_input", "parent": "COND-0002"},
            ]
        return [
            {"name": "INP-0001", "field_name": field_name, "parent": "COND-0001"},
        ]
    
    # STEP 2: Fetch OUTPUT SEQUENCE from parent
    def fetch_output_sequence(self, parent_name: str) -> List[Dict]:
        print(f"[Model] Fetching Output Sequence for parent: {parent_name}")
        if parent_name == "COND-0002":
            return [
                {"name": "OUT-0002", "field_name": "x_2_output", "parent": parent_name},
            ]
        return [
            {"name": "OUT-0001", "field_name": "x_output", "parent": parent_name},
        ]
    
    # STEP 5: Fetch CONDITION TYPE HEADER
    def fetch_condition_type(self, parent_names: List[str]) -> List[Dict]:
        print(f"[Model] Fetching Condition Type for parents: {parent_names}")
        
        headers = []
        
        if "COND-0001" in parent_names:
            headers.append({
                "name": "COND-0001",
                "type": "constant",
                "priority": 1,
                "depends_on": "COND-0002"
            })
        
        if "COND-0002" in parent_names:
            headers.append({
                "name": "COND-0002",
                "type": "constant",
                "priority": 2
            })
        
        return headers


class ViewModelFactory:
    _instances = {}

    @classmethod
    def get_controller(cls, key, clazz, doctype, event, event_fields):
        """Returns existing instance if available, else creates new one."""
        
        # Check if an instance already exists
        if key in cls._instances:
            result = cls._instances[key]
            return result

        instance = cls.instantiate_controller(cls, key, doctype, event, event_fields)
    
        return instance
    

    # function to Instantiate a new controllers
    def instantiate_controller(cls,key, doctype, event, event_fields):

        instance_controller = Controller(doctype, event, event_fields)
        instance_model = ClModelController(doctype,event, event_fields)
        instance_view = ClViewController(doctype, event, event_fields)

        cls._instances["controller"] = instance_controller
        cls._instances["view_controller"] = instance_model
        cls._instances["model_controller"] = instance_view

        instance_controller.set_model_and_view(instance_view, instance_model)
        instance_view.set_model_and_view(instance_view, instance_model)
        instance_model.set_model_and_view(instance_view, instance_model)

        return cls._instances[key]