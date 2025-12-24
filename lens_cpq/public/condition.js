$.each(frappe.boot.condition_type_doctypes, function (_i, d) {
    // this frappe.model.on was the logic behind fieldname trigger in frappe
    frappe.model.on(d, "*", function (fieldname, value, doc){
        frappe.call({
            method: "lens_cpq.conditions.entry_point.start_condition",
            args:{
                "doctype": d,
                "field_name": fieldname,
                "doc": doc
            },
            callback:function(idResponse){
                const laResult = idResponse.message
                // setting each condition type's output value
                for (const ldCondition of laResult){
                    for (const ldOutput of (ldCondition.outputs || [])){
                        frappe.model.set_value(
                            doc.doctype,
                            doc.name,
                            ldOutput.field_name,
                            ldOutput.value,
                            null,
                            true
                        );
                    } 
                }
            }
        });
    });
});