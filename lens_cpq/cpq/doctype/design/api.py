import frappe
from frappe import _

@frappe.whitelist()
def fn_get_formated_item_variants(item_name):
    """
    Optimized version: Fetch and format item attributes efficiently.
    """

    try:
        # Get item document and collect attribute names + default values
        item_doc = frappe.get_doc("Item", item_name)

        attribute_names = [attr.attribute for attr in item_doc.attributes]
        attribute_defaults = {attr.attribute: attr.attribute_value for attr in item_doc.attributes}

        if not attribute_names:
            return []

        # Fetch all item attributes in one query
        item_attributes = frappe.get_all(
            "Item Attribute",
            filters={"name": ["in", attribute_names]},
            fields=["name", "attribute_name", "numeric_values", "from_range", "to_range", "increment"],
            order_by="idx ASC"
        )

        # Fetch all related attribute values in one query
        attribute_values = frappe.get_all(
            "Item Attribute Value",
            filters={"parent": ["in", attribute_names]},
            fields=["parent", "attribute_value"],
            order_by="idx ASC"
        )

        # Organize attribute values by parent attribute name
        attribute_values_map = {}
        for val in attribute_values:
            attribute_values_map.setdefault(val.parent, []).append({
                "label": val.attribute_value,
                "value": val.attribute_value
            })

        # Prepare final field config list
        fields = []
        for attr in item_attributes:
            default_value = attribute_defaults.get(attr.attribute_name)

            field = {
                "label": attr.attribute_name,
                "fieldname": attr.attribute_name.replace(" ", "_").lower(),
                "numeric_values": attr.numeric_values,
                "from_range": attr.from_range,
                "to_range": attr.to_range,
                "increment": attr.increment,
                "default": default_value
            }

            if attr.numeric_values:
                field["fieldtype"] = "Range"
                field["min"] = attr.from_range
                field["max"] = attr.to_range
                field["step"] = attr.increment
            else:
                field["fieldtype"] = "Select"
                field["options"] = attribute_values_map.get(attr.name, [])

            fields.append(field)

        return fields

    except frappe.DoesNotExistError:
        frappe.throw(_("Item not found"))
    except Exception as e:
        frappe.log_error(frappe.get_traceback(), _("Error fetching item details"))
        frappe.throw(_("Could not fetch item details"))
