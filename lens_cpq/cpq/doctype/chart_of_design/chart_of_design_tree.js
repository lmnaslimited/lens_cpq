// Register treeview settings namespace if not already defined
frappe.provide("frappe.treeview_settings");

// Define treeview settings for the "Chart of Design" Doctype
frappe.treeview_settings["Chart of Design"] = {

    // Breadcrumb path shown at the top of the page
    breadcrumb: "Plant_Floor",

    // Title shown on the treeview page
    title: __("Chart of Design"),

    // Don't fetch root node by default (we'll handle root logic ourselves)
    get_tree_root: false,

    // Filters shown on the left panel
    filters: [
        {
            // Field to select Plant Floor
            fieldname: "plant_floor",
            fieldtype: "Link",
            options: "Plant Floor",  // Link Doctype
            label: __("Plant Floor"),

            // Triggered when the filter value changes
            on_change: function () {
                var lMe = frappe.treeview_settings["Chart of Design"].treeview;

                // Get selected plant floor value
                var lPlantFloor = lMe.page.fields_dict.plant_floor.get_value();

                // If no value is selected, throw error
                if (!lPlantFloor) {
                    frappe.throw(__("Please set a plant_floor"));
                }
            }
        }
    ],

    // Label to show for the root of the tree
    root_label: "Plant Floor",

    // Server method to fetch children nodes
    get_tree_nodes: "lens_cpq.cpq.doctype.chart_of_design.api.get_children",

    fields: [
        {
            fieldtype: "Check",
            fieldname: "is_group",
            label: __("Is Group"),
            description: __("Further characteristic can be made under Groups"),
        },
        {
            fieldtype: "Link",
            fieldname: "attribute",
            label: __("Attribute"),
            options: "Item Attribute",
            reqd: true,
            get_query: function () {
                return {
                    filters: {
                        numeric_values: 0,
                    },
                };
            },
        },
    ],

    toolbar: [
        {
            label: __("Add Group"),
            condition: function (node) {
                return node.expandable;
            },
            click: function (node) {
                const tree = frappe.views.trees["Chart of Design"];
                tree.make_new_node(node, true);
            },
            btnClass: "hidden-xs",
        },
        {
            label: __("Add Child"),
            condition: function (node) {
                return node.expandable;
            },
            click: function (node) {
                const tree = frappe.views.trees["Chart of Design"];
                tree.make_new_node(node, false);
            },
            btnClass: "hidden-xs",
        },
    ],

    onload: function (treeview) {
        frappe.treeview_settings["Chart of Design"].treeview = treeview

        treeview.make_new_node = function (parent_node, is_group) {
            let dialog = new frappe.ui.Dialog({
                title: __("Chart of Design"),

                fields: [
                    {
                        fieldtype: "Check",
                        fieldname: "is_group",
                        label: __("Is Group"),
                        description: __("Further characteristic can be made under Groups"),
                    },
                    {
                        fieldtype: "Link",
                        fieldname: "attribute",
                        label: __("Attribute"),
                        options: "Item Attribute",
                        reqd: true,
                        get_query: function () {
                            return {
                                filters: {
                                    numeric_values: 0,
                                },
                            };
                        },
                    },
                ],

                primary_action_label: __("Create"),
                primary_action: (values) => {
                    console.log("values", values)
                    frappe.call({
                        method: "lens_cpq.cpq.doctype.chart_of_design.api.add_node",
                        args: {
                            parent: parent_node.label,
                            attribute: values.attribute,
                            is_group: values.is_group,
                            is_root: parent_node.is_root || false
                        },
                        callback: function () {
                            treeview.tree.load_children(parent_node, true);
                            dialog.hide()
                        }
                    });
                }
            });

            dialog.set_value("is_group", is_group);

            if (is_group) {
                dialog.fields_dict.is_group.df.read_only = 1;
                dialog.fields_dict.is_group.refresh();
            } else {
                dialog.fields_dict.is_group.df.hidden = 1;
                dialog.fields_dict.is_group.refresh();

                dialog.fields_dict.attribute.get_query = function () {
                    return {};
                };
            }

            dialog.show();
        }
    },

    // Fields to ignore when determining parent-child relationship
    ignore_fields: ["parent_chart_of_design"]
};