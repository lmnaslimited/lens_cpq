import frappe

@frappe.whitelist()
# Whitelist this function to make it accessible via Frappe client calls (e.g., from JS)
# Function to get hierarchical children nodes for a given Doctype, optionally filtered by plant_floor or root
def get_children(i_doctype, i_parent=None, i_is_root=False, i_plant_floor=None, **kwargs):
    
    # Determine the parent field name dynamically (e.g., parent_machine_node)
    l_parent_fieldname = "parent_" + frappe.scrub(i_doctype)

    # Fields to return
    la_fields = [
        "name as value",
        "attribute",
        "abbr",
        "is_group as expandable",
        l_parent_fieldname,
        "lft",
        "rgt"
    ]

    # Filters
    la_filters = []

    # Handle root and non-root filtering
    if i_is_root:
        # Root nodes: no parent set
        la_filters.append([f"ifnull(`{l_parent_fieldname}`, '')", "=", "" if i_is_root else i_parent])
        if i_plant_floor:
            la_filters.append(["root_node", "=", i_plant_floor])
    else:
        # Children: filter by parent node
        la_filters.append([l_parent_fieldname, "=", i_parent])

    # Fetch the list of child nodes with the specified filters
    la_nodes = frappe.get_list(i_doctype, fields=la_fields, filters=la_filters)
     # Construct label
    for ld_node in la_nodes:
        ld_node["label"] = f"{ld_node.attribute} - {ld_node.abbr}" if ld_node.get("abbr") else ld_node.attribute

    # Return the list of nodes to the client
    return la_nodes
