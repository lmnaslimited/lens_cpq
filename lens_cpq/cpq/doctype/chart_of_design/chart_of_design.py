# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet
from frappe import _


# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet
from frappe import _

def generate_chart_of_design_name(parent_name, attribute):
    cod_exists = frappe.db.exists("Chart Of Design", parent_name)
    plant_floor_exists = frappe.db.exists("Plant Floor", parent_name)

    if cod_exists:
        cod_doc = frappe.get_doc("Chart Of Design", parent_name)
        abbr = cod_doc.abbr
        root_node = cod_doc.root_node 
    elif plant_floor_exists:
        plant_floor_doc = frappe.get_doc("Plant Floor", parent_name)
        abbr = plant_floor_doc.custom_abbreviation
        root_node = parent_name
    else:
        frappe.throw(_("Parent node not found in Chart Of Design or Plant Floor"))

    if not abbr:
        frappe.throw(_("Root abbreviation (abbr) not found for the parent"))

    name = f"{attribute} - {abbr}"
    return name, abbr, root_node

class ChartofDesign(NestedSet):
    def validate(self):
        parent = self.parent_chart_of_design or getattr(self, "parent", None) or self.root_node          

        new_name, root_abbr, root_node = generate_chart_of_design_name(parent, self.attribute)

        if self.name != new_name:
            self.name = new_name

        if not self.root_abbr:
            self.root_abbr = root_abbr

        if not self.root_node:
            self.root_node = root_node