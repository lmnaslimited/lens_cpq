from lens_cpq.condition_class.condition import ClInputFieldConditons

class ClConditionInputfieldCondtions(ClInputFieldConditons):
    def __init__(self, doctype, fieldname, value, condtionfieldRecord):
        super().__init__(doctype, fieldname, value, condtionfieldRecord)
    
    def evaluate(self):
        print(f"[ConditionInputField] Evaluating Condition for {self.fieldname} with value {self.value}")
        return True