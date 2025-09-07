from abc import ABC, abstractmethod, abstractproperty
from collections.abc import Callable
from typing import NewType
import frappe

ConditionType = NewType("ConditionType", list[dict])  # [{doctype: "Design",...}, ...]

class BaseClass(ABC):
    
    def get_condition_type(self, i_doctype: str) -> list[ConditionType]:
        '''
        Fetching all the Active Condition Type Manitained
        '''
        la_condition_types = frappe.get_all(
            "Condition Type", 
            filters={"document_reference": i_doctype, "enable":1},
            fields=["name","document_reference", "condition_type", "is_value_based",
                    "is_formula_based", "is_api_based", "priority",
                    "`tabInput Sequence`.field_name", "`tabInput Sequence`.field_type", "`tabInput Sequence`.length"],
            order_by="priority"
        )
        la_filter = set([ld_condition_type["name"] for ld_condition_type in la_condition_types])
        la_condition_value = frappe.get_all(
            "Condition Value", 
            filters={"condition_type": ["in", la_filter], "enable":1}, 
            fields=["*"],
            order_by="priority"
        )
        la_result = []
        # for ld_condition_type in la_condition_types:
        #     for ld_condition_value in la_condition_value:
        la_result.append(la_condition_types)

        return la_result
    
    def match_input_sequence_with_source():
        pass
    


class CondtionType(BaseClass):
    pass

@frappe.whitelist()
def condition_model(doctype:str):
    obj = CondtionType()
    return obj.get_condition_type(doctype)