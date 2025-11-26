from lens_cpq.condition_class.input_field_condition import ClInputFieldConditons
import frappe

class ClConstantInputfieldCondtions(ClInputFieldConditons):
    def __init__(self, engine, name, inputs, outputs):
        self.engine = engine
        self.model = engine.model
        self.inputs = inputs
        self.outputs = outputs
        self.name = name

    def evaluate(self):
        print("Evaluating:", self.inputs)
        return True

    def execute_output(self):
        print("Applying output:", self.outputs)
        # frappe.msgprint(f"Applying output:", self.outputs)
    