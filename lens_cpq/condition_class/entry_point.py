import frappe
from lens_cpq.condition_class.controller import ClViewController, Controller, ViewModelFactory, ClModelController

# for testing the class
# we will use this api in client script
@frappe.whitelist()
def start_condition():
    print("################## Starting Condition Controller Test #####################")
    # # the controller is the start
    # controller = Controller("Quotation", "on_update", ["on_change"])
    # # controller.init_controller()
    # controller.execute()

    # call controller
    # call view
    # call model
    # in controller set model and view (have a private / public method)
    # in view set model and view
    controller = ViewModelFactory.get_controller("controller", Controller,"Quotation", "on_update", ["on_change"])
    controller.execute()
    
    print("################## End Test ###############################")