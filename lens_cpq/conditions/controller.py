from lens_cpq.conditions.condition import cl_condtions
# from lens_cpq.conditions.input_condition_factory import cl_input_field_condition_factory
from lens_cpq.conditions.interface import if_controller
from typing import List, Union, Dict

import frappe
from collections import deque

class controller(if_controller):

    def __init__(self, i_doctype: str, i_event: str, i_fields: Union[list, str]):
        self.l_doctype = i_doctype
        self.l_event = i_event
        self.l_fields = i_fields
    
    def set_model_and_view(self, id_view_instance, id_model_instance):
        self.ld_view_controller = id_view_instance
        self.ld_model_controller = id_model_instance


    def execute(self, id_doc: Dict):
        # print(f"[Controller] Field changed: {self.l_fields}")
        self.la_result = self.ld_model_controller.execute()
        lo_engine = cl_condtions(id_doc)
        la_output = lo_engine.execute(self.la_result)
        self.ld_view_controller.execute(la_output, id_doc)
        

    
class cl_view_controller(controller):

    def is_sate_changed(self)->bool:
        return True
    
    def is_value_present_in_doc(self, ia_input_field_names:List)->bool:
        return True

    def execute(self, ia_output, id_doc):
        # print("[ViewController] Executing view logic")
        """
        Apply outputs on server-side doc and save
        """
        doc = frappe.get_doc(id_doc["doctype"], id_doc["name"])

        # Apply CPQ outputs
        for ld_condition in ia_output:
            for ld_output in ld_condition.get("outputs", []):
                doc.set(
                    ld_output["field_name"],
                    ld_output["value"]
                )
        if ia_output:
            doc.save()



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
        la_queue = deque([self.l_field_name])

        while la_queue:
            l_current_field = la_queue.popleft()

            la_inp_sequence = self.fetch_input_sequence(l_current_field)
            if not la_inp_sequence:
                continue

            l_parent = la_inp_sequence[0]["parent"]

            la_out_sequence = self.fetch_output_sequence(l_parent)
            if not la_out_sequence:
                continue

            la_collected.append({
                "parent": l_parent,
                "input_sequence": la_inp_sequence,
                "output_sequence": la_out_sequence,
                "condition_type": {},
                "rules": []     # IMPORTANT CHANGE
            })

            for ld_row in la_out_sequence:
                if ld_row.get("field_name"):
                    la_queue.append(ld_row["field_name"])

        # ---------------- FETCH CONDITION TYPES ---------------- #

        la_parents = [d["parent"] for d in la_collected]

        if not la_parents:
            return la_collected

        la_conditions = self.fetch_condition_type(la_parents)
        ld_condition_map = {c["name"]: c for c in la_conditions}

        # ---------------- BUILD RULES PER CONDITION VALUE ---------------- #

        for ld_record in la_collected:
            l_parent = ld_record["parent"]

            if l_parent not in ld_condition_map:
                continue

            ld_record["condition_type"] = ld_condition_map[l_parent]

            la_condition_values = self.fetch_condition_value(l_parent)

            la_rules = []

            for ld_cond_val in la_condition_values:
                l_cond_val_name = ld_cond_val["name"]

                la_rules.append({
                    "condition_value": l_cond_val_name,
                    "input_values": self.fetch_input_value(l_cond_val_name),
                    "output_values": self.fetch_output_value(l_cond_val_name)
                })

            ld_record["rules"] = la_rules

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
        ld_instance_model = cl_model_controller(i_doctype, i_event, i_fields)
        ld_instance_view = cl_view_controller(i_doctype, i_event, i_fields)

        cls._ld_instances["controller"] = ld_instance_controller
        cls._ld_instances["view_controller"] = ld_instance_model
        cls._ld_instances["model_controller"] = ld_instance_view

        ld_instance_controller.set_model_and_view(ld_instance_view, ld_instance_model)
        # ld_instance_view.set_model_and_view(ld_instance_view, ld_instance_model)
        # ld_instance_model.set_model_and_view(ld_instance_view, ld_instance_model)

        return cls._ld_instances[i_key]