from abc import ABC, abstractmethod
from typing import List, Any, Literal

# controller interface
class Ifcontroller(ABC):
    @abstractmethod
    def execute(self):
        pass

#fieldcondition interface
# child table instance
class Iffieldcondtions(ABC):
    type: Literal["api", "formula", "constant", "condition"]
    doctype: str
    field_name: str
    input_value: Any
    condtion_field_record: dict

    @abstractmethod
    def evaluate(self) -> bool:
        pass

# condition interface
# one condition type record
class IfCondtions(ABC):
    Condtion_type: str
    Input_sequence: Any
    Input_values: Any
    input_fields: List[Iffieldcondtions] # input fields instances
    output_sequece: Any
    output_fields: List[Iffieldcondtions]
    Output_value: Any

    
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