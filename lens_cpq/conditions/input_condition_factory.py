# from lens_cpq.condition_class.condition_input_condition import ClConditionInputfieldCondtions
# from lens_cpq.condition_class.api_input_condition import ClApiInputfieldCondtions
# from lens_cpq.condition_class.formula_input_condition import ClFormulaInputfieldCondtions
from lens_cpq.conditions.constant_input_condition import cl_constant_input_field_condtions
from lens_cpq.conditions.constant_output_condition import cl_constant_output_evaluator
# from lens_cpq.condition_class.condition import ClInputFieldConditons
# from typing import Dict, Any

# class cl_input_field_condition_factory:
   
#    def build(result):
#         if i_cond_type == "constant":
#             return cl_constant_input_field_condtions(io_engine=io_engine,
#             i_name=i_cond_name,
#             ia_inputs=ia_input_records,
#             ia_outputs=ia_output_records)


class cl_input_evaluator_factory:

    @staticmethod
    def get_evaluator(i_type):
        if i_type == "Constant":
            return cl_constant_input_field_condtions()
        # elif i_type == "Formula":
        #     return cl_formula_input_evaluator()
        # elif i_type == "API":
        #     return cl_api_input_evaluator()
        else:
            raise ValueError(f"Unsupported input type: {i_type}")

class cl_output_evaluator_factory:

    @staticmethod
    def get_evaluator(i_type):
        if i_type == "Constant":
            return cl_constant_output_evaluator()
        # elif i_type == "Formula":
        #     return cl_formula_output_evaluator()
        # elif i_type == "API":
        #     return cl_api_output_evaluator()
        else:
            raise ValueError(f"Unsupported output type: {i_type}")

