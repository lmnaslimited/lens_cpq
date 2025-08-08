# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.utils.nestedset import NestedSet
from frappe import _

"""
    Purpose - Generate a name for a Chart of Design node based on its parent and attribute.
    @i_parent_name {str} - Name of the parent node (could be Chart of Design or Plant Floor).
    @i_attribute {str}  - Attribute name to include in the generated name.
    Output - Returns a tuple of (generated name, abbreviation, root node name).
"""
def fn_generate_chart_of_design_name(i_parent_name, i_attribute):

    l_cod_exists = frappe.db.exists("Chart of Design", i_parent_name)

    l_plant_floor_exists = frappe.db.exists("Plant Floor", i_parent_name)

    # Check if parent exists as a Chart of Design node
    if l_cod_exists:
        # Fetch the Chart of Design parent document
        ld_cod_doc = frappe.get_doc("Chart of Design", i_parent_name)

        # Get abbreviation from the parent Chart of Design document
        l_abbr = ld_cod_doc.root_abbr

        # Get root node reference from the parent Chart of Design document
        l_root_node = ld_cod_doc.root_node 

    # Check if parent exists as a Plant Floor node
    elif l_plant_floor_exists:
        # Fetch the Plant Floor parent document
        ld_plant_floor_doc = frappe.get_doc("Plant Floor", i_parent_name)

        # Get custom abbreviation from the Plant Floor document
        l_abbr = ld_plant_floor_doc.custom_abbreviation

        # Since parent is Plant Floor, root node is the parent itself
        l_root_node = i_parent_name

    else:
        # Throw error if parent not found in either doctype
        frappe.throw(_("Parent node not found in Chart Of Design or Plant Floor"))

    
    # Ensure abbreviation exists
    if not l_abbr:
        frappe.throw(_("Root abbreviation (abbr) not found for the parent"))

    # Generate the new name combining attribute and abbreviation
    l_name = f"{i_attribute} - {l_abbr}"

    return l_name, l_abbr, l_root_node


class ChartofDesign(NestedSet):  

    def before_insert(self):
        # Populate attribute_value with all values from Item Attribute
        if self.attribute:
            ld_values = frappe.get_all(
                "Item Attribute Value",
                filters={
                    "parent": self.attribute,
                    "parenttype": "Item Attribute"
                },
                fields=["attribute_value"]
            )
            # Join all values into a newline-separated string
            self.attribute_value = "\n".join([i_value.attribute_value for i_value in ld_values])
    
    def validate(self):
        # If custom parent field is set then use it as parent
        if self.parent_chart_of_design:
            l_parent = self.parent_chart_of_design
        # Else if generic parent attribute exists and is not None then use it as parent
        elif hasattr(self, "parent") and self.parent is not None:
             l_parent = self.parent
        # Otherwise use the root node as parent
        else:
            l_parent = self.root_node        

        # Generate name, root abbreviation and root node based on parent and current attribute
        l_new_name, l_root_abbr, l_root_node = fn_generate_chart_of_design_name(l_parent, self.attribute)

        # Update the document name if it differs from the generated name
        if self.name != l_new_name:
            self.name = l_new_name

        # Set root abbreviation if not already set
        if not self.root_abbr:
            self.root_abbr = l_root_abbr

        # Set root node if not already set
        if not self.root_node:
            self.root_node = l_root_node

        # Prevent numeric attributes from being set as group nodes
        if self.is_group and self.increment:
            frappe.throw("Cannot convert numeric attribute to a group node.")