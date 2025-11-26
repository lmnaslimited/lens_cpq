from abc import ABC, abstractmethod
from typing import Any, Dict
from lens_cpq.condition_class.interface import Iffieldcondtions


class ClInputFieldConditons(Iffieldcondtions, ABC):
    def __init__(self, doctype:str, field_name:str, value:Any, condtion_field_record: Dict, engine, cond_name):
        self.doctype = doctype
        self.field_name = field_name
        self.value = value
        self.condtion_field_record = condtion_field_record
        self.engine = engine   # <— store engine here
        self.model = engine.model  # <— model available
        self.fields = engine.fields
        self.cond_name = cond_name
    
    @abstractmethod
    def evaluate(self):
        pass