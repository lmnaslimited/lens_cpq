from lens_cpq.condition.base_condition import BaseCondition
from lens_cpq.condition.condition_execution_manager import ConditionExecutionManager
import frappe

class ConditionEvaluator(BaseCondition):
    def __init__(self, doc):
        super().__init__(doc)

    def evaluate(self):
        condition_records = self.fn_get_condition_values()
        return condition_records
    
    def execute(self):
        pass


def before_save(doc, event):
    condition = ConditionEvaluator(doc)
    evaluate = condition.evaluate()
    if evaluate:
        doc.job_title = evaluate[0]["priority"]
        frappe.msgprint(str(evaluate[0]["priority"]))
    else:
        frappe.msgprint("No condition records found")