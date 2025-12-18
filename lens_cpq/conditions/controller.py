from lens_cpq.conditions.condition import cl_condtions
# from lens_cpq.conditions.input_condition_factory import cl_input_field_condition_factory
from lens_cpq.conditions.interface import if_controller
from typing import List, Union, Dict

import frappe
from collections import deque

class controller(if_controller):

    def __init__(self, i_doctype: str, i_event: str, i_fields: Union[list, str], id_doc: Dict):
        self.l_doctype = i_doctype
        self.l_event = i_event
        self.l_fields = i_fields
        self.ld_doc = id_doc
    
    def set_model_and_view(self, id_view_instance, id_model_instance):
        self.ld_view_controller = id_view_instance
        self.ld_model_controller = id_model_instance


    def execute(self):
        # print(f"[Controller] Field changed: {self.l_fields}")
        self.la_result = self.ld_model_controller.execute()
        engine = cl_condtions(self.ld_doc)
        engine.execute(self.la_result)

    
class cl_view_controller(controller):

    def is_sate_changed(self)->bool:
        return True
    
    def is_value_present_in_doc(self, ia_input_field_names:List)->bool:
        return True

    def execute(self):
        print("[ViewController] Executing view logic")
    

class cl_model_controller(controller):
    def execute(self):
        # print("[ModelController] Executing model logic...")
        return model(self.l_fields).execute()
    

class model(if_controller):
    def __init__(self, i_field_name):
        self.l_field_name = i_field_name
        
    def execute(self):
        return self.resolve_condition_chain()
        
    def resolve_condition_chain(self):
        la_collected = []
        la_queue = deque([self.l_field_name])  # Process multiple field names

        while la_queue:
            l_current_field = la_queue.popleft()

            # 1. Fetch input sequence for the field
            la_inp_sequence = self.fetch_input_sequence(l_current_field)
            if not la_inp_sequence:
                continue

            # Parent is always same in all rows (since filter is by field_name)
            l_parent = la_inp_sequence[0]["parent"]

            # 2. Fetch output sequence based on parent
            la_out_sequence = self.fetch_output_sequence(l_parent)
            if not la_out_sequence:
                continue

            # 3. Collect the record
            la_collected.append({
                "parent": l_parent,
                "input_sequence": la_inp_sequence,
                "output_sequence": la_out_sequence,
                "condition_type": [],   # placeholder (will fill later)
                "input_value": [],
                "output_value": []
            })

            # 4. Add all output field_names to queue for further processing
            for ld_row in la_out_sequence:
                l_next_field = ld_row["field_name"]
                if l_next_field:  # avoid null
                    la_queue.append(l_next_field)

        # 5. Fetch condition types for ALL parents in collected list
        la_parents = [ld_record["parent"] for ld_record in la_collected]

        if la_parents:
            la_conditions = self.fetch_condition_type(la_parents)

            # 6. Attach condition type to the correct parent
            ld_condition_map = {ld_condition["name"]: ld_condition for ld_condition in la_conditions}
            for ld_record in la_collected:
                l_parent_name = ld_record["parent"]
                if l_parent_name in ld_condition_map:
                    ld_record["condition_type"] = ld_condition_map[l_parent_name]
                    la_condition_values = self.fetch_condition_value(l_parent_name)

                    # 7. Fetch input & output values for each condition value
                    la_input_vals, la_output_vals = [], []
                    for ld_cond in la_condition_values:
                        l_cond_name = ld_cond["name"]
                        la_input_vals.extend(self.fetch_input_value(l_cond_name))
                        la_output_vals.extend(self.fetch_output_value(l_cond_name))

                    ld_record["input_value"] = la_input_vals
                    ld_record["output_value"] = la_output_vals


        return la_collected
    
    def fetch_input_sequence(self, i_field_name) -> List[Dict]:
        la_get_input_sequence = frappe.get_all("Input Sequence",
                                               filters={"field_name": i_field_name},
                                               fields=["name","field_name","parent","type"])
        return la_get_input_sequence
    
    def fetch_output_sequence(self, i_parent_name: str) -> List[Dict]:
        la_get_output_sequence = frappe.get_all("Output Sequence",
                                               filters={"parent": i_parent_name},
                                               fields=["name","field_name","parent","type"])
        return la_get_output_sequence

    def fetch_condition_type(self, ia_parent_names: List[str]) -> List[Dict]:
        la_condition_type = frappe.get_list("Condition Type",
                                            filters={"name": ["in", ia_parent_names]},
                                            fields=["name", "document_reference", "condition_type", "priority"],
                                            order_by="priority asc")
        
        return la_condition_type
    
    def fetch_condition_value(self, i_condition_name):
        la_condition_value = frappe.get_list("Condition Value",
                                            filters={"condition_type": i_condition_name},
                                            fields=["name"])
        
        return la_condition_value
    
    def fetch_input_value(self, ia_condition_value):
        la_get_input_value = frappe.get_all("Input Condition Value",
                                               filters={"parent": ia_condition_value},
                                               fields=["name","field_name","value", "parent"])
        return la_get_input_value
    
    def fetch_output_value(self, ia_condition_value):
        la_get_output_value = frappe.get_all("Output Condition Value",
                                               filters={"parent": ia_condition_value},
                                               fields=["name","field_name","value", "parent"])
        return la_get_output_value



class fc_view_model_factory:
    _ld_instances = {}

    @classmethod
    def get_controller(cls, i_key, i_doctype, i_event, i_fields, id_doc):
        """Returns existing instance if available, else creates new one."""
        
        # Check if an instance already exists
        if i_key in cls._ld_instances:
            ld_result = cls._ld_instances[i_key]
            return ld_result

        ld_instance = cls.instantiate_controller(cls, i_key, i_doctype, i_event, i_fields, id_doc)
    
        return ld_instance
    

    # function to Instantiate a new controllers
    def instantiate_controller(cls, i_key, i_doctype, i_event, i_fields, id_doc):

        ld_instance_controller = controller(i_doctype, i_event, i_fields, id_doc)
        ld_instance_model = cl_model_controller(i_doctype, i_event, i_fields, id_doc)
        ld_instance_view = cl_view_controller(i_doctype, i_event, i_fields, id_doc)

        cls._ld_instances["controller"] = ld_instance_controller
        cls._ld_instances["view_controller"] = ld_instance_model
        cls._ld_instances["model_controller"] = ld_instance_view

        ld_instance_controller.set_model_and_view(ld_instance_view, ld_instance_model)
        ld_instance_view.set_model_and_view(ld_instance_view, ld_instance_model)
        ld_instance_model.set_model_and_view(ld_instance_view, ld_instance_model)

        return cls._ld_instances[i_key]