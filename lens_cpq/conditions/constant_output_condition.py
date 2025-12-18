class cl_constant_output_evaluator:
    def apply(self, ld_output, doc):
        doc.set(ld_output["field_name"], ld_output["value"])
