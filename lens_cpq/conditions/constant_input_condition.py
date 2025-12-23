# from lens_cpq.conditions.input_field_condition import cl_input_field_conditons
import frappe
# cl_input_field_conditons is implemented here
class cl_constant_input_field_condtions:
    # def __init__(self, io_engine, i_name, ia_inputs, ia_outputs):
    #     self.lo_engine = io_engine
    #     self.lo_model = io_engine.ld_model
    #     self.la_inputs = ia_inputs
    #     self.la_outputs = ia_outputs
    #     self.l_name = i_name

    def valuate(self):
        print("Evaluating:", self.la_inputs)
        return True

    # def execute_output(self):
    #     print("Applying output:", self.la_outputs)
    #     # frappe.msgprint(f"Applying output:", self.outputs)

    def evaluate(self, ld_input, doc):
        field = ld_input["field_name"]
        expected = ld_input["value"]
        return doc.get(field) == expected #here we want field_name but the input value store the label so this validation will be failed
    