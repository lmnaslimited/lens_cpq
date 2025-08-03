import frappe
from frappe.utils import cint

@frappe.whitelist()
# Whitelist this function to make it accessible via Frappe client calls (e.g., from JS)
# Function to get hierarchical children nodes for a given Doctype, optionally filtered by plant_floor or root
# Incoming variable on runtime by framework
def get_children(doctype, parent=None, is_root=False, plant_floor=None, **kwargs):
    
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


@frappe.whitelist()
def add_node(args=None):
    from frappe.desk.treeview import make_tree_args

    if not args:
        args = frappe.local.form_dict

    args.doctype = "Chart of Design"

    args = make_tree_args(**args)

    chart = frappe.new_doc("Chart of Design")

    if args.get("ignore_permissions"):
        chart.flags.ignore_permissions = True
        args.pop("ignore_permissions")

    chart.update(args)

    if not chart.parent_chart_of_design:
        chart.parent_chart_of_design = args.get("parent")

    chart.old_parent = ""

    chart.is_group = cint(chart.is_group) or 0

    if cint(chart.get("is_root")):
        chart.parent_chart_of_design = None
        chart.flags.ignore_mandatory = True

    chart.insert()

    return chart.name