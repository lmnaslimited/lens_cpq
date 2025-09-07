# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.utils.nestedset import NestedSet
from frappe.utils import cstr, flt

"""
    Generate a standardized name for a Chart of Design node.

    Args:
        i_parent_name (str): Parent node name (could be from Chart of Design or Plant Floor).
        i_attribute (str): Attribute name to include in the generated node name.

    Returns: tuple: (generated_name, abbreviation, root_node_name)
"""
def fn_generate_chart_of_design_name(i_parent_name, i_attribute):

    # Check if parent exists in Chart of Design
    l_cod_exists = frappe.db.exists("Chart of Design", i_parent_name)

    # Check if parent exists in Plant Floor
    l_plant_floor_exists = frappe.db.exists("Plant Floor", i_parent_name)

    if l_cod_exists:
        # Fetch root abbreviation and root node from Chart of Design
        [l_abbr, l_root_node] = frappe.db.get_value(
            "Chart of Design", 
            {"name": i_parent_name},
            ["root_abbr", "root_node"]
        )

    elif l_plant_floor_exists:
        # Fetch abbreviation from Plant Floor
        l_abbr = frappe.db.get_value("Plant Floor", {"name": i_parent_name}, ["custom_abbreviation"])
        l_root_node = i_parent_name
    
    else:
        # Error: Parent not found in Chart of Design or Plant Floor
        frappe.throw(_("Parent node not found in Chart Of Design or Plant Floor"))

    if not l_abbr:
        # Error: Root abbreviation missing for parent
        frappe.throw(_("Root abbreviation (abbr) not found for the parent"))

    # Construct new node name using attribute and abbreviation
    l_name = f"{i_attribute} - {l_abbr}"

    return l_name, l_abbr, l_root_node


class ChartofDesign(NestedSet):  

    def after_insert(self):
        """
        After inserting a Chart of Design node:
        Populate `attribute_value` child table with values
        from the linked Item Attribute.
        """
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

        # Else use generic parent if available
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

        if self.is_group and self.increment > 0:
            # Error: Raised when a numeric attribute is being marked as a group node
            frappe.throw("Cannot convert numeric attribute to a group node.")

        # --- Validation for numeric attributes ---
        
        if self.increment > 0:
            """
                Validate whether a given value follows the defined increment steps.
                Args:
                    i_from_range (float): Minimum allowed range.
                    i_increment (float): Increment step size.
                    i_value (float): Value to validate.
                    i_attribute (str): Attribute name.
                    i_fieldname (str): Field name for error message.
            """
            def fn_validate_is_incremental(i_from_range, i_increment, i_value, i_attribute, i_fieldname):
                # Since we are using same field "default_value" to store both
                # Non numeric and Numeric Default value, we need to check
                # apha-numeric condition for Numeric attribute as precaution
                try:
                    float(i_value)
                except ValueError:
                    frappe.throw(
                        _("{0} for Attribute {1} must be a numeric value")
                        .format(i_fieldname, i_attribute)
                    )
                l_precision = max(len(cstr(v).split(".")[-1].rstrip("0")) for v in (i_value, i_increment))
                l_remainder = flt((flt(i_value) - i_from_range) % i_increment, l_precision)
                l_incremental = l_remainder == 0 or l_remainder == i_increment

                if not l_incremental:
                    # Error: Raised when value does not align with increment steps
                    frappe.throw(
                        _("{0} for Attribute {1} must follow increments of {2} starting from {3}")
                        .format(i_fieldname, i_attribute, i_increment, i_from_range)
                    )

            # Fetch ranges and increment from linked Item Attribute
            l_from_range, l_to_range, l_increment = frappe.get_value(
                "Item Attribute",
                self.attribute,  
                ["from_range", "to_range", "increment"]
            )

            if self.from_range < l_from_range or self.from_range > l_to_range:
                # Error: Raised when `from_range` is outside the allowed min/max bounds of the linked Item Attribute.
                frappe.throw(f"'From Range' must be between {l_from_range} and {l_to_range}")

            if self.to_range < l_from_range or self.to_range > l_to_range:
                # Error: Raised when `to_range` is outside the allowed min/max bounds of the linked Item Attribute.
                frappe.throw(f"'To Range' must be between {l_from_range} and {l_to_range}")

            if self.from_range >= self.to_range:
                # Error: Raised when `from_range` is greater than or equal to `to_range`.
                frappe.throw(f"'From Range' must be less than 'To Range' {l_to_range}")

            if self.default_value:
                # Validate `default_value` increments
                fn_validate_is_incremental(l_from_range, l_increment, self.default_value, self.attribute, "Default Value")
                if not (l_from_range <= flt(self.default_value) <= l_to_range):
                    # Error: Raised when `default_value` is outside the allowed min/max bounds of the linked Item Attribute.
                    frappe.throw(f"Default Value {self.default_value} is outside the allowed range {l_from_range} - {l_to_range}")

            # Validate `from_range` and `to_range` increments
            if self.increment > 0:
                fn_validate_is_incremental(l_from_range, l_increment, self.from_range, self.attribute, "From Range")
                fn_validate_is_incremental(l_from_range, l_increment, self.to_range, self.attribute, "To Range")
        
        else:
      
        # --- Validation for non-numeric attributes ---
           
            if self.default_value:
                la_included_values = [
                    l_value.attribute_value 
                    for l_value in self.attribute_value 
                    if not l_value.exclude
                ]
                
                # if not la_included_values:
                #     # Error: Raised when all attribute values are excluded
                #     frappe.throw("At least one attribute should not be excluded.")

                if self.default_value not in la_included_values:
                    # Error: Raised when the chosen `default_value` marked as excluded
                    frappe.throw(f"Default value '{self.default_value}' cannot be excluded.")