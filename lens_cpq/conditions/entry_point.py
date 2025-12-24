import frappe
from lens_cpq.conditions.controller import fc_view_model_factory
import json

# for testing the class
# we will use this api in client script
@frappe.whitelist()
def start_condition(doctype, field_name, doc):
    if isinstance(doc, str):
        doc =  json.loads(doc)
    # print("################## Starting Condition Controller Test #####################")
    controller = fc_view_model_factory.get_controller("controller",doctype, "on_change", field_name)
    return controller.execute(doc)
    
    # print("################## End Test ###############################")