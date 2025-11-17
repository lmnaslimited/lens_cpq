import frappe
from frappe.utils import cint

@frappe.whitelist()
"""
    Return hierarchical nodes for a given DocType to support tree-based UI rendering.

    This function retrieves child nodes based on the specified parent and root-level
    configuration. It also merges attribute metadata (value, abbr, exclude) into a
    grouped node structure that aligns with Frappe's TreeView requirements.

    Args:
        doctype (str): The DocType to fetch nodes from.
        parent (str): Parent node identifier.
        is_root (bool): Indicates whether root-level nodes should be fetched.
        plant_floor (str): Selected Plant Floor.

    Returns:
        list[dict]: List of consolidated node dictionaries formatted for TreeView.
"""
def fn_get_children(doctype, parent=None, is_root=False, plant_floor=None, **kwargs):
    
    # Determine the parent field name dynamically (e.g., parent_machine_node)
    l_parent_fieldname = "parent_" + frappe.scrub(doctype)

    # Fields to return
    la_fields = [
        "name as value",
        "is_group as expandable",
        "root_abbr",
        l_parent_fieldname,
        "attribute",
        "from_range",
        "to_range",
        "increment",
        "default_value",
        "`tabCPQ Item Attribute Value`.attribute_value",
        "`tabCPQ Item Attribute Value`.abbr",
        "`tabCPQ Item Attribute Value`.exclude",
    ]

    # Filters
    la_filters = []

    # Handle root and non-root filtering
    if is_root:
        # Root nodes: no parent set
        la_filters.append([f"ifnull(`{l_parent_fieldname}`, '')", "=", "" if is_root else parent])
        if plant_floor:
            la_filters.append(["root_node", "=", plant_floor])
    else:
        # Children: filter by parent node
        la_filters.append([l_parent_fieldname, "=", parent])
    
    # Fetch the list of child nodes with the specified filters
    la_nodes = frappe.get_list(doctype, fields=la_fields, filters=la_filters)

    ld_grouped_nodes = {}

    # Iterate through the fetched node records and consolidate attribute values
    for ld_row in la_nodes:
        # Unique identifier for grouping
        l_key = ld_row["value"]  

        #  If node is seen for the first time:  initialize its consolidated structure
        if l_key not in ld_grouped_nodes:
            ld_node = ld_row.copy()

            # Container for aggregated attribute-values
            ld_node["attribute_value"] = []  
            
            # Construct label using attribute and abbreviation
            ld_node["label"] = f"{ld_row['attribute']} - {ld_row['root_abbr']}" if ld_row.get("root_abbr") else ld_row["attribute"]

            # Remove first copy of child table fields
            ld_node.pop("abbr", None)
            ld_node.pop("exclude", None)

            ld_grouped_nodes[l_key] = ld_node

        #   Insert each attribute-value pair into the node’s grouped list
        if ld_row.get("attribute_value"):
            ld_grouped_nodes[l_key]["attribute_value"].append({
                "attribute_value": ld_row["attribute_value"],
                "abbr": ld_row["abbr"],
                "exclude": ld_row["exclude"]
            })

    return list(ld_grouped_nodes.values())

"""
    Purpose: Adds a new node to the 'Chart of Design' tree structure..
    @args (dict): Dictionary containing node data. If not provided,
    data is taken from the request form_dict.
    Output: The name of the newly created 'Chart of Design' document.
"""
@frappe.whitelist()
def fn_add_node(args=None):
    from frappe.desk.treeview import make_tree_args

    # If no args provided explicitly - use form input values
    if not args:
        args = frappe.local.form_dict

    # Set doctype to Chart of Design
    args.doctype = "Chart of Design"

    # Prepare arguments compatible with tree structure
    args = make_tree_args(**args)

    # Create a new Chart of Design document
    ld_chart = frappe.new_doc("Chart of Design")

    # If ignore_permissions flag is passed, set it and remove from args
    if args.get("ignore_permissions"):
        ld_chart.flags.ignore_permissions = True
        args.pop("ignore_permissions")

    # Update the new document
    ld_chart.update(args)

    # If parent_chart_of_design is not set - assign from args
    if not ld_chart.parent_chart_of_design:
        ld_chart.parent_chart_of_design = args.get("parent")

    # Clear old_parent reference 
    ld_chart.old_parent = ""

    # Ensure is_group is stored as an integer (0 or 1)
    ld_chart.is_group = cint(ld_chart.is_group) or 0

    # If node is marked as root - remove parent and ignore mandatory fields
    if cint(ld_chart.get("is_root")):
        ld_chart.parent_chart_of_design = None
        ld_chart.flags.ignore_mandatory = True

    # Insert the new document into the database
    ld_chart.insert()

    # Return the document name of the newly created node
    return ld_chart.name
