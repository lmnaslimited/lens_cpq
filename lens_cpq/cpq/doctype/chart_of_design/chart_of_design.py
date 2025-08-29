# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet
from frappe.utils import cstr, flt

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
        [l_abbr, l_root_node] = frappe.db.get_value(
            "Chart of Design", 
            {"name": i_parent_name},
            ["root_abbr", "root_node"]
        )

    # Check if parent exists as a Plant Floor node
    elif l_plant_floor_exists:
        l_abbr = frappe.db.get_value("Plant Floor", {"name": i_parent_name}, ["custom_abbreviation"])
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

    def after_insert(self):
        # Populate attribute_value with all values from Item Attribute
        if self.attribute:
            ld_values = frappe.get_all(
                "Item Attribute Value",
                filters={
                    "parent": self.attribute,
                    "parenttype": "Item Attribute"
                },
                fields=["attribute_value","abbr", "idx"],
                order_by="idx"
            )
            for l_values in ld_values:
                self.append(
                    "attribute_value",
                    {
                        "attribute_value":l_values.attribute_value,
                        "abbr":l_values.abbr
                    }
                )
            self.save()
    
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
        if self.is_group and self.increment > 0:
            frappe.throw("Cannot convert numeric attribute to a group node.")

        if self.increment > 0:
            def validate_is_incremental(from_range, increment, value, attribute, fieldname):
                precision = max(len(cstr(v).split(".")[-1].rstrip("0")) for v in (value, increment))
                remainder = flt((flt(value) - from_range) % increment, precision)

                is_incremental = remainder == 0 or remainder == increment

                if not is_incremental:
                    frappe.throw(
                        _("{0} for Attribute {1} must follow increments of {2} starting from {3}")
                        .format(fieldname, attribute, increment, from_range)
                    )

            l_from_range, l_to_range, l_increment = frappe.get_value(
                "Item Attribute",
                self.attribute,  
                ["from_range", "to_range", "increment"]
            )

            if self.from_range < l_from_range or self.from_range > l_to_range:
                frappe.throw(f"'From Range' must be between {l_from_range} and {l_to_range}")

            if self.to_range < l_from_range or self.to_range > l_to_range:
                frappe.throw(f"'To Range' must be between {l_from_range} and {l_to_range}")

            if self.from_range >= self.to_range:
                frappe.throw(f"'From Range' must be less than 'To Range' ({self.to_range})")

            if self.default_value:
                validate_is_incremental(l_from_range, l_increment, self.default_value, self.attribute, "Default Value")
                if not (l_from_range <= flt(self.default_value) <= l_to_range):
                    frappe.throw(f"Default Value {self.default_value} is outside the allowed range {l_from_range} - {l_to_range}")

            if self.increment > 0:
                validate_is_incremental(l_from_range, l_increment, self.from_range, self.attribute, "From Range")
                validate_is_incremental(l_from_range, l_increment, self.to_range, self.attribute, "To Range")

        else: 
            if self.default_value:
                included_value = []
                for value in self.attribute_value:
                    if not value.exclude:
                        included_value.append(value)
            
                if self.default_value not in included_value:
                    frappe.throw(f"(Warning: {self.default_value} is default value)")
                        


                  