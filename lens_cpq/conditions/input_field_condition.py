from abc import ABC, abstractmethod
from typing import Any, Dict
from lens_cpq.conditions.interface import if_field_condtions


class cl_input_field_conditons(if_field_condtions, ABC):
    def __init__(self, i_doctype:str, i_field_name:str, i_value:Any, id_condtion_field_record: Dict, io_engine, i_cond_name):
        self.l_doctype = i_doctype
        self.l_field_name = i_field_name
        self.l_value = i_value
        self.ld_condtion_field_record = id_condtion_field_record
        self.lo_engine = io_engine   # <— store engine here
        self.ld_model = io_engine.ld_model  # <— model available
        self.l_fields = io_engine.l_fields
        self.l_cond_name = i_cond_name
    
    @abstractmethod
    def evaluate(self):
        pass