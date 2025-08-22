// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

frappe.ui.form.on("Chart of Design", {
    refresh(frm) {
        console.log(frm.doc)
        // Show "Convert to Group" for child node which is non numeric attribute
        if (!frm.doc.increment && !frm.doc.is_group == 1) {
            frm.add_custom_button(__('Convert to Group'), function () {
                frm.set_value('is_group', 1);
                frm.save();
            }, __("Actions"));
        }

        // Show "Convert to Child" only if group and has no children
        if (frm.doc.is_group == 1) {
            frappe.call({
                method: "frappe.client.get_count",
                args: {
                    doctype: "Chart of Design",
                    filters: {
                        parent_chart_of_design: frm.doc.name
                    }
                },
                callback: function (res) {
                    if (res.message == 0) {
                        frm.add_custom_button(__('Convert to Child'), function () {
                            frm.set_value('is_group', 0);
                            frm.save();
                        }, __("Actions"));
                    }
                }
            });
        }

        if (frm.doc.increment == 0 && frm.doc.item_attribute_value.length > 0) {
            let attribute_values = frm.doc.item_attribute_value
                .filter(values => values.exclude == 0)
                .map(values => values.attribute_value);

            // Set all values as options in the select field
            frm.set_df_property("default_option", "options", attribute_values);
        }
    },
});