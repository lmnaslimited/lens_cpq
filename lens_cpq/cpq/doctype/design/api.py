import frappe
from frappe import _

@frappe.whitelist()
def fn_get_formated_item_variants(item_name):
    """
    Fetches and formats the attributes for a given item.

    This API retrieves attributes associated with an item and returns them as a structured list. 
    Each attribute is represented as a field configuration, specifying whether it is a range-based 
    field or a select-type field. The configuration includes default values, options, and range specifications where applicable.

    Parameters:
        item_name (str): The name of the item for which attributes need to be fetched.

    Returns:
        list[dict]: A list of dictionaries representing attribute field configurations. 
        Each dictionary includes:
            - label, name ,type ,numeric_values ,min ,max ,step ,default ,options 

    Raises:
        DoesNotExistError: If the specified item does not exist.
        Exception: If any other error occurs, the error is logged and a user-friendly message is thrown.
    """
    try:
        # Get item document and collect attribute names + default values
        ld_item_doc = frappe.get_doc("Item", item_name)

        la_attribute_names = [ld_attribute.attribute for ld_attribute in ld_item_doc.attributes]
        ld_attribute_defaults = {ld_attribute.attribute: ld_attribute.attribute_value for ld_attribute in ld_item_doc.attributes}

        if not la_attribute_names:
            return []

        # Fetch all item attributes in one query
        la_item_attributes = frappe.get_all(
            "Item Attribute",
            filters={"name": ["in", la_attribute_names]},
            fields=["name", "attribute_name", "numeric_values", "from_range", "to_range", "increment"],
            order_by="idx ASC"
        )

        # Fetch all related attribute values in one query
        la_attribute_values = frappe.get_all(
            "Item Attribute Value",
            filters={"parent": ["in", la_attribute_names]},
            fields=["parent", "attribute_value"],
            order_by="idx ASC"
        )

        # Organize attribute values by parent attribute name
        ld_attribute_values_map = {}
        for ld_value in la_attribute_values:
            ld_attribute_values_map.setdefault(ld_value.parent, []).append({
                "label": ld_value.attribute_value,
                "value": ld_value.attribute_value
            })

        # Prepare final field config list
        la_fields = []
        for ld_attribute in la_item_attributes:
            l_default_value = ld_attribute_defaults.get(ld_attribute.attribute_name)

            ld_field = {
                "label": ld_attribute.attribute_name,
                "fieldname": ld_attribute.attribute_name.replace(" ", "_").lower(),
                "numeric_values": ld_attribute.numeric_values,
                "from_range": ld_attribute.from_range,
                "to_range": ld_attribute.to_range,
                "increment": ld_attribute.increment,
                "default": l_default_value
            }

            if ld_attribute.numeric_values:
                ld_field["fieldtype"] = "Range"
                ld_field["min"] = ld_attribute.from_range
                ld_field["max"] = ld_attribute.to_range
                ld_field["step"] = ld_attribute.increment
            else:
                ld_field["fieldtype"] = "Select"
                ld_field["options"] = ld_attribute_values_map.get(ld_attribute.name, [])

            la_fields.append(ld_field)

        return la_fields

    except frappe.DoesNotExistError:
        frappe.throw(_("Item not found"))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching item details"))
        frappe.throw(_("Could not fetch item details"))