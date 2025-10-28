from abc import ABC, abstractmethod
import frappe

class BaseCondition(ABC):
    def __init__(self, doc=None):
        self.doc = doc
        self.doctype = doc.doctype

    def fn_get_condition_types(self):
        """
        Get all the condition type that are active for the
        incoming doctype
        """
        l_a_condition_types = frappe.get_all(
            "Condition Type", 
            filters={"enable":1, "document_reference": self.doctype},
            fields=[]
            )
        # etracting the name alone
        l_a_cond_type = []
        for l_d_cond_type in l_a_condition_types:
            l_a_cond_type.append(l_d_cond_type.name)
        return l_a_cond_type
    
    def fn_get_condition_values(self):
        """
        Get all the condition value for the respective
        condition type in the priority order
        """
        get_condition_type = self.fn_get_condition_types()
        """
        Input Condition Value and Output Condition Value
        has Same fields "field_name" and "value"
        so on get_all the output's field is overriding the input's key
        """
        l_a_condition_values = frappe.get_all(
            "Condition Value",
            filters={"condition_type":["in", get_condition_type], "enable":1},
            fields=["name", "priority"],
            order_by="priority"
            )
        l_a_input_values = frappe.get_all(
            "Input Condition Value",
            filters={"parent": ["in", [cv["name"] for cv in l_a_condition_values]]},
            fields=["parent", "field_name", "value"]
        )

        l_a_output_values = frappe.get_all(
            "Output Condition Value",
            filters={"parent": ["in", [cv["name"] for cv in l_a_condition_values]]},
            fields=["parent", "field_name", "value"]
        )
        l_a_merged_record = []
        for cv in l_a_condition_values:
            l_a_merged_record.append({
                "name": cv["name"],
                "priority": cv["priority"],
                "input_conditions": [
                    inp for inp in l_a_input_values if inp["parent"] == cv["name"]
                ],
                "output_conditions": [
                    out for out in l_a_output_values if out["parent"] == cv["name"]
                ]
            })
        return l_a_merged_record

    def fn_transform_dict_to_array(self, i_d_data)->list[dict]:

        return 

    def fn_transform_condition_records(self, i_d_condition_value):
        pass

    @abstractmethod
    def evaluate(self):
        pass
    
    @abstractmethod
    def execute(self):
        pass