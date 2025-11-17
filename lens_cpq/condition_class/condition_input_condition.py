from lens_cpq.condition_class.condition import ClInputFieldConditons

class ClConditionInputfieldCondtions(ClInputFieldConditons):
    def __init__(self, doctype, field_name, value, condition_field_record):
        super().__init__(doctype, field_name, value, condition_field_record)
    
    def evaluate(self):
        print(f"[ConditionInputField] Evaluating Condition for {self.field_name} with value {self.value}")
        return True