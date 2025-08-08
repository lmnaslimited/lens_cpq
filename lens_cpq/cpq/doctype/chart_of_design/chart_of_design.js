// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

frappe.ui.form.on("Chart of Design", {
    refresh(frm) {

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
    },
});