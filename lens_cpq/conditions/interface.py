from abc import ABC, abstractmethod
from typing import List, Any, Literal

# controller interface
class if_controller(ABC):
    @abstractmethod
    def execute(self):
        pass

#fieldcondition interface
# child table instance
class if_field_condtions(ABC):
    l_type: Literal["api", "formula", "constant", "condition"]
    l_doctype: str
    l_field_name: str
    l_input_value: Any
    ld_condtion_field_record: dict

    @abstractmethod
    def evaluate(self) -> bool:
        pass

# condition interface
# one condition type record
class if_condtions(ABC):
    l_condtion_type: str
    la_input_sequence: List
    la_input_values: List
    la_input_fields: List[if_field_condtions] # input fields instances
    la_output_sequece: List
    la_output_fields: List[if_field_condtions]
    la_Output_values: List

    
    def get_condtion_type(self):
        pass
    
    
    def get_condtion_input_value(self):
        pass

    
    def get_condtion_output_value(self):
        pass

    @abstractmethod
    def evaluate_output(self):
        pass

    @abstractmethod
    def is_condition_true(self)-> bool:
        pass