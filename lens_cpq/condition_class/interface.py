from abc import ABC, abstractmethod
from typing import List, Any, Literal

# controller interface
class Ifcontroller(ABC):
    @abstractmethod
    def execute(self):
        pass

#fieldcondition interface
class Iffieldcondtions(ABC):
    type: Literal["api", "formula", "constant", "condition"]
    doctype: str
    fieldname: str
    inputvalue: Any
    condtionfieldRecord: dict

    @abstractmethod
    def evaluate(self) -> bool:
        pass

# condition interface
class IfCondtions(ABC):
    Condtiontype: Any
    InputSequence: Any
    Inputvalues: Any
    inputfields: List[Iffieldcondtions]
    outputsequece: Any
    outputfields: List[Iffieldcondtions]
    Outputvalue: Any

    
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
    def is_condition_true(self):
        pass