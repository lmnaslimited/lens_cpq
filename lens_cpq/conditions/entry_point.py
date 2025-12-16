import frappe
from lens_cpq.conditions.controller import fc_view_model_factory

# for testing the class
# we will use this api in client script
@frappe.whitelist()
def start_condition():
    # print("################## Starting Condition Controller Test #####################")
    controller = fc_view_model_factory.get_controller("controller","Lead", "on_change", "Lead Type")
    controller.execute()
    
    # print("################## End Test ###############################")