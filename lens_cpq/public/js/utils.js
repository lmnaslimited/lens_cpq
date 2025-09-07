// Show Condition Type dashboard
$(document).on("app_ready", function () {
	$.each(frappe.boot.condition_type_doctypes, function (_i, d) {
		frappe.ui.form.on(d, {
			onload: function (frm) {				
				
			},

			refresh: function (frm) {
                console.log("this is from public js")
                frappe.call({
					method: "lens_cpq.cpq.model.base_class.condition_model",
					args: {
						doctype: frm.doc.doctype,
					},
					callback: function (r) {
						if (r && r.message) {
                            console.log(r.message)
                        }
                    }
                })
            }
		});
	});
});