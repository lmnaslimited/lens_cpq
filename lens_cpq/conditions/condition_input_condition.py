from lens_cpq.conditions.condition import cl_input_field_conditons

class cl_condition_input_field_condtions(cl_input_field_conditons):
    def __init__(self, doctype, field_name, value, condition_field_record):
        super().__init__(doctype, field_name, value, condition_field_record)
    
    def evaluate(self):
        print(f"[ConditionInputField] Evaluating Condition for {self.field_name} with value {self.value}")
        return True