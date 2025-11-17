from abc import ABC, abstractmethod
from typing import Any, Dict
from lens_cpq.condition_class.interface import IfCondtions, Iffieldcondtions

# its an abstract class that implements IfCondtions
class ClCondtions(IfCondtions, ABC):
    def __init__(self, condition_type: str, doctype: str, event_fields: Dict[str, Any] = None):
        self.condition_type = condition_type
        self.doctype = doctype
        self.event_fields = event_fields or {}
        
    def is_condition_true(self) -> bool:
        print(f"[ClCondtions] Checking condition truth for {self.condition_type}")
        return True

    @abstractmethod
    def execute_output(self) -> Any:
        pass
    

    
class ClInputFieldConditons(Iffieldcondtions, ABC):
    def __init__(self, doctype:str, field_name:str, value:Any, condtion_field_record: Dict):
        self.doctype = doctype
        self.field_name = field_name
        self.value = value
        self.condtion_field_record = condtion_field_record
    
    @abstractmethod
    def evaluate(self):
        pass