from abc import ABC
from lens_cpq.conditions.input_condition_factory import (
    cl_input_evaluator_factory,
    cl_output_evaluator_factory
)
from lens_cpq.conditions.interface import if_condtions


class cl_condtions(if_condtions):

    def __init__(self, id_doc):
        self.doc = id_doc
    def evaluate_output(self):
        pass
    def is_condition_true(self)-> bool:
        pass
    # --------------------------------------------------
    # ENTRY POINT
    # --------------------------------------------------

    def execute(self, la_collected):
        """
        Executes condition evaluation.

        la_collected structure:
        [
            {
                parent,
                condition_type,
                rules: [
                    {
                        condition_value,
                        input_values,
                        output_values
                    }
                ]
            }
        ]
        """
        la_executed = []

        for ld_condition_type in la_collected:
            la_outputs = self._execute_condition_type(ld_condition_type)

            if la_outputs:
                la_executed.append({
                    "parent": ld_condition_type["parent"],
                    "outputs": la_outputs
                })

        return la_executed

    # --------------------------------------------------
    # CONDITION TYPE
    # --------------------------------------------------

    def _execute_condition_type(self, ld_condition_type):
        """
        Executes all rules (condition values) under one condition type
        Returns collected outputs
        """
        la_outputs = []

        for ld_rule in ld_condition_type.get("rules", []):
            if self._is_rule_true(ld_rule):
                la_outputs.extend(self._collect_rule_outputs(ld_rule))

        return la_outputs

    # --------------------------------------------------
    # RULE (CONDITION VALUE)
    # --------------------------------------------------

    def _is_rule_true(self, ld_rule) -> bool:
        """
        ALL input_values of a rule must evaluate to True
        """
        for ld_input in ld_rule.get("input_values", []):
            if not self._evaluate_single_input(ld_input):
                return False
        return True

    # --------------------------------------------------
    # INPUT EVALUATION
    # --------------------------------------------------

    def _evaluate_single_input(self, ld_input):
        l_type = ld_input.get("type", "Constant")
        evaluator = cl_input_evaluator_factory.get_evaluator(l_type)
        return evaluator.evaluate(ld_input, self.doc)

    # --------------------------------------------------
    # OUTPUT APPLICATION
    # --------------------------------------------------

    def _collect_rule_outputs(self, ld_rule):
        """
        Returns output instructions instead of applying them
        """
        la_outputs = []

        for ld_output in ld_rule.get("output_values", []):
            l_type = ld_output.get("type", "Constant")
            evaluator = cl_output_evaluator_factory.get_evaluator(l_type)
            la_outputs.append(evaluator.apply(ld_output))  # NO doc

        return la_outputs
