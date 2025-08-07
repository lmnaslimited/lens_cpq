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

    // Fields shown in dialog while adding node
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
            // While fetching attribute list - apply filter to show only attributes with non-numeric values
            get_query: function () {
                return {
                    filters: {
                        numeric_values: 0,
                    },
                };
            },
        },
    ],

    // Buttons shown in toolbar
    toolbar: [
        {
            label: __("Add Group"),

            // Show button only for expandable nodes
            condition: function (node) {
                return node.expandable;
            },

            // While clicking - open dialog to add group node
            click: function (node) {
                const ldTree = frappe.views.trees["Chart of Design"];
                ldTree.fnMakeNewNode(node, true);
            },
            btnClass: "hidden-xs",
        },
        {
            label: __("Add Child"),

            // Show button only for expandable nodes
            condition: function (node) {
                return node.expandable;
            },

            // While clicking - open dialog to add child node
            click: function (node) {
                const ldTree = frappe.views.trees["Chart of Design"];
                ldTree.fnMakeNewNode(node, false);
            },
            btnClass: "hidden-xs",
        },
    ],

    // While treeview loads - store treeview reference and define new node logic
    onload: function (ldTreeview) {
        frappe.treeview_settings["Chart of Design"].treeview = ldTreeview;

        /*
       * Purpose - Show a dialog to create a new node in the Chart of Design tree.
       * @iParentNode {Object} - Node under which the new node is added.
       * @iIsGroup {Boolean} - Flag indicating if the new node is a group (true) or a child (false).
       * Output - On successful creation, the new node is inserted under the parent and tree is refreshed.
       */
        ldTreeview.fnMakeNewNode = function (iParentNode, iIsGroup) {
            // Open dialog to create new node
            let lDialog = new frappe.ui.Dialog({
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

                        // While fetching attribute list - apply filter to show only attributes with non-numeric values
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

                // While clicking create - call server method to create new node
                primary_action: (idFormValues) => {
                    frappe.call({
                        method: "lens_cpq.cpq.doctype.chart_of_design.api.fn_add_node",
                        args: {
                            parent: iParentNode.label,
                            attribute: idFormValues.attribute,
                            is_group: idFormValues.is_group,
                            is_root: iParentNode.is_root || false
                        },
                        callback: function (ldRes) {
                            // If no error - reload tree and close dialog
                            if (ldRes) {
                                ldTreeview.tree.load_children(iParentNode, true);
                                lDialog.hide();
                            }
                        }
                    });
                }
            });

            // Set default is_group value and make read-only
            lDialog.set_value("is_group", iIsGroup);
            lDialog.fields_dict.is_group.df.read_only = 1;
            lDialog.fields_dict.is_group.refresh();

            // If node is child - remove attribute filter          
            if (!iIsGroup) {
                lDialog.fields_dict.attribute.get_query = function () {
                    return {};
                };
            }

            // Show dialog
            lDialog.show();
        };
    },
    // Fields to ignore when determining parent-child relationship
    ignore_fields: ["parent_chart_of_design"]
};