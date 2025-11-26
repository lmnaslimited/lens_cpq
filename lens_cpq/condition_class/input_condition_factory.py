# from lens_cpq.condition_class.condition_input_condition import ClConditionInputfieldCondtions
# from lens_cpq.condition_class.api_input_condition import ClApiInputfieldCondtions
# from lens_cpq.condition_class.formula_input_condition import ClFormulaInputfieldCondtions
from lens_cpq.condition_class.constant_input_condition import ClConstantInputfieldCondtions
# from lens_cpq.condition_class.condition import ClInputFieldConditons
from typing import Dict, Any

class InputFieldConditionFactory:
   
   def build(cond_type, cond_name, input_records, output_records, engine):
        if cond_type == "constant":
            return ClConstantInputfieldCondtions(engine=engine,
            name=cond_name,
            inputs=input_records,
            outputs=output_records)
