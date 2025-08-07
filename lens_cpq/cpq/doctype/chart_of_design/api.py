import frappe
from frappe.utils import cint

@frappe.whitelist()
# Whitelist this function to make it accessible via Frappe client calls (e.g., from JS)
# Function to get hierarchical children nodes for a given Doctype, optionally filtered by plant_floor or root
# Incoming variable on runtime by framework
def fn_get_children(doctype, parent=None, is_root=False, plant_floor=None, **kwargs):
    
    # Determine the parent field name dynamically (e.g., parent_machine_node)
    l_parent_fieldname = "parent_" + frappe.scrub(doctype)

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
     # Construct label
    for ld_node in la_nodes:
        ld_node["label"] = f"{ld_node.attribute} - {ld_node.abbr}" if ld_node.get("abbr") else ld_node.attribute

    # Return the list of nodes to the client
    return la_nodes

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
