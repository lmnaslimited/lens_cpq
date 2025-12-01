# from lens_cpq.condition_class.condition_input_condition import ClConditionInputfieldCondtions
# from lens_cpq.condition_class.api_input_condition import ClApiInputfieldCondtions
# from lens_cpq.condition_class.formula_input_condition import ClFormulaInputfieldCondtions
from lens_cpq.conditions.constant_input_condition import cl_constant_input_field_condtions
# from lens_cpq.condition_class.condition import ClInputFieldConditons
from typing import Dict, Any

class cl_input_field_condition_factory:
   
   def build(i_cond_type, i_cond_name, ia_input_records, ia_output_records, io_engine):
        if i_cond_type == "constant":
            return cl_constant_input_field_condtions(io_engine=io_engine,
            i_name=i_cond_name,
            ia_inputs=ia_input_records,
            ia_outputs=ia_output_records)
