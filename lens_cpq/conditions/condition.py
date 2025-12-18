from abc import ABC, abstractmethod
from typing import Any, Dict, List
# from lens_cpq.conditions.controller import FCViewModelFactory
from lens_cpq.conditions.input_condition_factory import cl_input_evaluator_factory, cl_output_evaluator_factory
from lens_cpq.conditions.interface import if_condtions
import frappe

# its an abstract class that implements IfCondtions
class cl_condtions(if_condtions):
    def __init__(self, id_doc):
        # self.condition_type = condition_type
        # self.l_doctype = i_doctype
        # self.l_fields = i_fields
        # self.l_event = i_event
        # self.ld_model = id_model
        # self.ld_view = id_view
        self.doc = id_doc

    def is_condition_true(self) -> bool:
        # print(f"[ClCondtions] Checking condition truth for {self.condition_type}")
        pass
    
    def evaluate_output(self):
        pass
    
    def execute(self, la_collected):
        """
        Entry point.
        Evaluates inputs → applies outputs.
        """
        la_executed = []

        # # Sort by priority (lower number = higher priority)
        # la_collected.sort(
        #     key=lambda x: x.get("condition_type", {}).get("priority", 999)
        # )

        for ld_condition in la_collected:
            if self._evaluate_inputs(ld_condition):
                self._process_outputs(ld_condition)
                la_executed.append(ld_condition)

        return la_executed

    # ---------------- INPUT PROCESSING ---------------- #

    def _evaluate_inputs(self, ld_condition):
        """
        ALL input values must evaluate to True
        """
        for ld_input in ld_condition.get("input_value", []):
            if not self._evaluate_single_input(ld_input):
                return False
        return True

    def _evaluate_single_input(self, ld_input):
        l_type = ld_input.get("type", "Constant")
        evaluator = cl_input_evaluator_factory.get_evaluator(l_type)
        return evaluator.evaluate(ld_input, self.doc)

    # ---------------- OUTPUT PROCESSING ---------------- #

    def _process_outputs(self, ld_condition):
        for ld_output in ld_condition.get("output_value", []):
            l_type = ld_output.get("type", "Constant")
            evaluator = cl_output_evaluator_factory.get_evaluator(l_type)
            evaluator.apply(ld_output, self.doc)