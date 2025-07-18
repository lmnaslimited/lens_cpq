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

    // Fields to ignore when determining parent-child relationship
    ignore_fields: ["parent_chart_of_design"]
};