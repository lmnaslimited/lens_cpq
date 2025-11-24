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
    controller = ViewModelFactory.get_controller("controller", Controller,"Quotation", "on_update", ["on_change"])
    # call view
    view = ViewModelFactory.get_controller("view_controller", ClViewController,"Quotation", "on_update", ["on_change"])
    # call model
    model = ViewModelFactory.get_controller("model_controller", ClModelController,"Quotation", "on_update", ["on_change"])

    # in controller set model and view (have a private / public method)
    controller.set_model_and_view(view, model)
    # in view set model and view
    view.set_model_and_view(view, model)
    model.set_model_and_view(view, model)
    print("################## End Test ###############################")