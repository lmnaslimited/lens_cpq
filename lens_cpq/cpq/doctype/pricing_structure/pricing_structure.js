// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Pricing Structure", {
// 	refresh(frm) {

// 	},
// });

let ldMeta = null
frappe.ui.form.on("Pricing Structure", {
    onload: function (frm) {
        if (frm.doc.reference_doctype) {
            frm.trigger('reference_doctype');
        }

        // If child_table_field already has value, trigger child_target_field logic
        if (frm.doc.child_table_field) {
            frm.trigger('child_table_field');
        }
    },

    reference_doctype: function (frm) {
        frappe.model.with_doctype(frm.doc.reference_doctype, function () {
            ldMeta = frappe.get_meta(frm.doc.reference_doctype);

            // Populate Currency fields for parent target field
            const laCurrencyFields = ldMeta.fields
                .filter(f => f.fieldtype === 'Currency')
                .map(f => f.fieldname);
           
            // Populate child table options
            const laTableFields = ldMeta.fields
                .filter(f => f.fieldtype === 'Table')
                .map(f => f.fieldname);

            frm.set_df_property('parent_target_field', 'options', laCurrencyFields.join('\n'));
            frm.set_df_property('child_table_field', 'options', laTableFields.join('\n'));
            frm.refresh_fields(['child_table_field', 'parent_target_field']);
        });
    },

    child_table_field: function (frm) {
        if (!frm.doc.reference_doctype || !frm.doc.child_table_field) return;

        const ldParentMeta = ldMeta || frappe.get_meta(frm.doc.reference_doctype);
        const ldChildField = ldParentMeta.fields.find(
            f => f.fieldname === frm.doc.child_table_field && f.fieldtype === 'Table'
        );

        if (!ldChildField || !ldChildField.options) return;

        // Now load child table Doctype to extract its Currency fields
        frappe.model.with_doctype(ldChildField.options, function () {
            const ldChildMeta = frappe.get_meta(ldChildField.options);
            const laCurrencyFields = ldChildMeta.fields
                .filter(f => f.fieldtype === 'Currency')
                .map(f => f.fieldname);

            frm.set_df_property('child_target_field', 'options', laCurrencyFields.join('\n'));
            frm.refresh_field('child_target_field');
        });
    }
})