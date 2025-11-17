from lens_cpq.condition_class.condition_input_condition import ClConditionInputfieldCondtions
from lens_cpq.condition_class.api_input_condition import ClApiInputfieldCondtions
from lens_cpq.condition_class.formula_input_condition import ClFormulaInputfieldCondtions
from lens_cpq.condition_class.constant_input_condition import ClConstantInputfieldCondtions
from lens_cpq.condition_class.condition import ClInputFieldConditons
from typing import Dict, Any

class InputFieldConditionFactory:
    @staticmethod
    def create(doctype: str, field_name: str, value: Any, condition_field_record: Dict[str, Any]) -> ClInputFieldConditons:
        eval_type = condition_field_record.get("field_evalutionType", "").lower()
        print(f"[Factory] Creating input field condition for type: {eval_type}")
        if eval_type == "constant":
            return ClConstantInputfieldCondtions(doctype, field_name, value, condition_field_record)
        elif eval_type == "api":
            return ClApiInputfieldCondtions(doctype, field_name, value, condition_field_record)
        elif eval_type == "formula":
            return ClFormulaInputfieldCondtions(doctype, field_name, value, condition_field_record)
        elif eval_type == "condition":
            return ClConditionInputfieldCondtions(doctype, field_name, value, condition_field_record)
        else:
            raise ValueError(f"Unknown field_evalutionType: {eval_type}")
