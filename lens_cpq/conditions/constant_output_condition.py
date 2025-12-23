class cl_constant_output_evaluator:
    def apply(self, ld_output):
         return {
            "field_name": ld_output["field_name"],
            "value": ld_output["value"]
        }

