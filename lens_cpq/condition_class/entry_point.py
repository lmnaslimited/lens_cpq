import frappe
from lens_cpq.condition_class.controller import ClViewController, Controller, ViewModelFactory, ClModelController

# for testing the class
# we will use this api in client script
@frappe.whitelist()
def start_condition():
    print("################## Starting Condition Controller Test #####################")
    controller = ViewModelFactory.get_controller("controller", Controller,"Quotation", "on_change", "status")
    controller.execute()
    
    print("################## End Test ###############################")