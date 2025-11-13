from lens_cpq.condition_class.condition import ClInputFieldConditons

class ClFormulaInputfieldCondtions(ClInputFieldConditons):
    def __init__(self, doctype, fieldname, value, condtionfieldRecord):
        super().__init__(doctype, fieldname, value, condtionfieldRecord)
    
    def evaluate(self):
        print(f"[FormulaInputField] Evaluating Formula for {self.fieldname} with value {self.value}")
        return True