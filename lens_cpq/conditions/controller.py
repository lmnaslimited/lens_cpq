from lens_cpq.conditions.condition import ClCondtions
from lens_cpq.conditions.interface import if_controller
from typing import List, Union, Dict
from lens_cpq.conditions.interface import if_condtions
# Classes in Python names should follow the CapWords (or CamelCase) convention
class controller(if_controller):

    ld_view_controller: if_controller
    ld_model_controller: if_controller
    l_doctype: str
    l_event: str
    l_fields: Union[list, str] #one field or array of field

    def __init__(self, i_doctype: str, i_event: str, i_fields: Union[list, str]):
        self.l_doctype = i_doctype
        self.l_event = i_event
        self.l_fields = i_fields
    
    def set_model_and_view(self, id_view_instance, id_model_instance):
        self.ld_view_controller = id_view_instance
        self.ld_model_controller = id_model_instance


    def execute(self):
        print(f"[Controller] Field changed: {self.l_fields}")
        ld_condition = ClCondtions(self.l_doctype, self.l_event, self.l_fields, self.ld_view_controller,self.ld_model_controller)
       
        la_affected_conditions = ld_condition.resolve_condition_chain(
            self.l_fields, self.l_event
        )

        ld_condition.execute_conditions(la_affected_conditions)

    
class cl_view_controller(controller):

   
    def __init__(self, i_doctype, i_event, i_fields):
        super().__init__(i_doctype, i_event, i_fields) 
        
    def is_sate_changed(self)->bool:
        return True
    
    def is_value_present_in_doc(self, ia_input_field_names:List)->bool:
        return True

    def execute(self):
        print("[ViewController] Executing view logic")
    
    def set_model_and_view(self, id_view_instance, id_model_instance):
        self.ld_view_controller = id_view_instance
        self.ld_model_controller = id_model_instance
        

class cl_model_controller(controller):
    la_conditions: List[if_condtions]
    
    def __init__(self, i_doctype, i_event, i_fields):
        super().__init__(i_doctype, i_event, i_fields)
        
    def execute(self):
        print("[ModelController] Executing model logic...")
    
    def set_model_and_view(self, id_view_instance, id_model_instance):
        self.ld_view_controller = id_view_instance
        self.ld_model_controller = id_model_instance

    # STEP 1: Fetch INPUT SEQUENCE records
    def fetch_input_sequence(self, i_field_name: str) -> List[Dict]:
        print(f"[Model] Fetching Input Sequence for: {i_field_name}")
        if i_field_name == "x_output":
            return [
                {"name": "INP-0002", "field_name": "2_input", "parent": "COND-0002"},
            ]
        return [
            {"name": "INP-0001", "field_name": i_field_name, "parent": "COND-0001"},
        ]
    
    # STEP 2: Fetch OUTPUT SEQUENCE from parent
    def fetch_output_sequence(self, i_parent_name: str) -> List[Dict]:
        print(f"[Model] Fetching Output Sequence for parent: {i_parent_name}")
        if i_parent_name == "COND-0002":
            return [
                {"name": "OUT-0002", "field_name": "x_2_output", "parent": i_parent_name},
            ]
        return [
            {"name": "OUT-0001", "field_name": "x_output", "parent": i_parent_name},
        ]
    
    # STEP 5: Fetch CONDITION TYPE HEADER
    def fetch_condition_type(self, ia_parent_names: List[str]) -> List[Dict]:
        print(f"[Model] Fetching Condition Type for parents: {ia_parent_names}")
        
        la_headers = []
        
        if "COND-0001" in ia_parent_names:
            la_headers.append({
                "name": "COND-0001",
                "type": "constant",
                "priority": 1,
                "depends_on": "COND-0002"
            })
        
        if "COND-0002" in ia_parent_names:
            la_headers.append({
                "name": "COND-0002",
                "type": "constant",
                "priority": 2
            })
        
        return la_headers


class fc_view_model_factory:
    _ld_instances = {}

    @classmethod
    def get_controller(cls, i_key, i_doctype, i_event, i_fields):
        """Returns existing instance if available, else creates new one."""
        
        # Check if an instance already exists
        if i_key in cls._ld_instances:
            ld_result = cls._ld_instances[i_key]
            return ld_result

        ld_instance = cls.instantiate_controller(cls, i_key, i_doctype, i_event, i_fields)
    
        return ld_instance
    

    # function to Instantiate a new controllers
    def instantiate_controller(cls, i_key, i_doctype, i_event, i_fields):

        ld_instance_controller = controller(i_doctype, i_event, i_fields)
        ld_instance_model = cl_model_controller(i_doctype,i_event, i_fields)
        ld_instance_view = cl_view_controller(i_doctype, i_event, i_fields)

        cls._ld_instances["controller"] = ld_instance_controller
        cls._ld_instances["view_controller"] = ld_instance_model
        cls._ld_instances["model_controller"] = ld_instance_view

        ld_instance_controller.set_model_and_view(ld_instance_view, ld_instance_model)
        ld_instance_view.set_model_and_view(ld_instance_view, ld_instance_model)
        ld_instance_model.set_model_and_view(ld_instance_view, ld_instance_model)

        return cls._ld_instances[i_key]