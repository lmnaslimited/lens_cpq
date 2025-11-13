import frappe
from lens_cpq.condition_class.controller import Controller

@frappe.whitelist()
def start_condition():
    print("################## Starting Condition Controller Test #####################")
    controller = Controller("Quotation", "on_update", ["on_change"])
    controller.execute()
    print("################## End Test ###############################")