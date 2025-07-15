# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

# import frappe

import frappe
from frappe.model.document import Document
from frappe.utils.safe_exec import safe_eval


def fn_dispatch_pricing_if_needed(doc, method):
    la_pricing_structures = frappe.get_all("Pricing Structure", filters={
        "reference_doctype": doc.doctype
    }, order_by="creation desc", limit=1)

    if not la_pricing_structures:
        return

    ld_pricing_str_doc = frappe.get_doc("Pricing Structure", la_pricing_structures[0].name) #currently took 1 but need to be looped
    ld_pricing_str_doc.fn_apply_pricing(doc)


class PricingStructure(Document):
    def fn_apply_pricing(self, doc): #here self is a class variable
        """Apply pricing logic to parent or child rows"""
        if self.child_table_field:
            # Child-level application
            la_child_table = getattr(doc, self.child_table_field, []) #getattr ( will fetch the row details)
            for ld_row in la_child_table:
                ld_result = self.fn_evaluate(runtime_doc=doc, row=ld_row)
                l_target = self.child_target_field
                if l_target and hasattr(ld_row, l_target):
                    setattr(ld_row, l_target, ld_result.get("final_price"))
        else:
            # Parent-level application
            ld_result = self.fn_evaluate(runtime_doc=doc)
            if self.target_field and hasattr(doc, self.target_field):
                setattr(doc, self.target_field, ld_result.get("final_price"))

    def fn_evaluate(self, runtime_doc=None, row=None):
        ld_contex = {}

        # Inject parent doc and optional child row into context
        if runtime_doc:
            ld_contex.update(runtime_doc.as_dict())
        if row:
            ld_contex.update(row.as_dict())
            ld_contex['row'] = row.as_dict()
        ld_contex['doc'] = runtime_doc.as_dict() if runtime_doc else {}

        l_total = 0
        ld_applied_components = {}

        for ld_seq_row in self.sequence:
            try:
                ld_pricing_component = frappe.get_doc("Pricing Component", ld_seq_row.pricing_component) 
                l_label_key = ld_pricing_component.label.strip().lower().replace(" ", "_") #can use variable name too since we have include it in doctype

                # Dynamic variable logic
                if ld_pricing_component.is_dynamic and ld_pricing_component.api_function and ld_pricing_component.variable_name:
                    try:
                    
                        # only done for ui APIs but can extend to whitlist method
                        ld_script = frappe.get_doc("Server Script", ld_pricing_component.api_function)
                        if ld_script.disabled:
                            frappe.throw(_("Server Script {0} is disabled").format(ld_pricing_component.api_function))

                        frappe.local.form_dict.doc = runtime_doc 
                        frappe.local.form_dict.row = row

                        l_dynamic_value = ld_script.execute_method()
                        ld_contex[ld_pricing_component.variable_name] = l_dynamic_value
                    except Exception as e:
                        frappe.log_error(f"Dynamic API error in '{ld_pricing_component.label}': {e}")
                        continue

                # Condition evaluation
                l_apply = True
                if ld_pricing_component.condition:
                    try:
                        l_apply = safe_eval(ld_pricing_component.condition, ld_contex)  #safe evaal from slaary slip code
                    except Exception as e:
                        frappe.log_error(f"Condition error in '{ld_pricing_component.label}': {e}")
                        l_apply = False

                if not l_apply:
                    continue

                # Formula or constant
                l_amount = 0
                if ld_pricing_component.formula:
                    try:
                        l_amount = safe_eval(ld_pricing_component.formula, ld_contex)
                    except Exception as e:
                        frappe.log_error(f"Formula error in '{ld_pricing_component.label}': {e}")
                        l_amount = 0
                elif ld_pricing_component.constant is not None:
                    l_amount = ld_pricing_component.constant

                ld_contex[l_label_key] = l_amount
                l_total += l_amount
                ld_applied_components[ld_pricing_component.label] = l_amount

            except Exception as e:
                frappe.log_error(f"Component evaluation failed: {e}")
                continue

        self.final_price = l_total
        ld_contex["final_price"] = l_total

        return {
            "final_price": l_total,
            "components": ld_applied_components,
            "context": ld_contex
        }
