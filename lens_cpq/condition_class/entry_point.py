import frappe
from lens_cpq.condition_class.controller import Controller

# for testing the class
# we will use this api in client script
@frappe.whitelist()
def start_condition():
    print("################## Starting Condition Controller Test #####################")
    # the controller is the start
    controller = Controller("Quotation", "on_update", ["on_change"])
    # controller.init_controller()
    controller.execute()
    print("################## End Test ###############################")