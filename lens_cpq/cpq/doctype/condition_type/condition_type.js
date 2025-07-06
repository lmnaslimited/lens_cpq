// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Condition Type", {
// 	refresh(frm) {

// 	},
// });

frappe.ui.form.on('Condition Type', {
    // When the 'document_reference' field changes
    document_reference(frm) {
        // Clear the input_sequence and output_sequence tables
        frm.set_value('input_sequence', []);
        frm.set_value('output_sequence', []);
    },
    refresh(frm){
        if(frm.doc.document_reference){
            fnPopulateFieldOptions(frm, 'input_sequence', 'field_name');
            fnPopulateFieldOptions(frm, 'output_sequence', 'field_name');
        }
    }
});

//commentedfor cpq demo
// Modular function to fetch metadata for the selected document type
// function fnGetMetaData(frm, callback) {
//     frappe.call({
//         method: "get_meta", // server-side api method to call
//         args: {
//             i_doctype: frm.doc.document_reference // pass the selected document reference
//         },
//         callback: function (response) {
//             callback(response.message); // return the metadata fields through callback
//         }
//     });
// }

function fnGetMetaData(frm, callback) {
    if (frm.doc.document_reference === "Design") {
        // Custom logic to fetch Item Attributes for "Design"
        frappe.call({
            method: "frappe.client.get_list",
            args: {
                doctype: "Item Attribute",
                fields: ["attribute_name"],
                limit_page_length: 0
            },
            callback: function(response) {
                // Convert to array of objects with label and fieldtype similar to get_meta structure
                const attributes = response.message.map(attr => ({
                    label: attr.attribute_name,
                    fieldtype: "Data" // You can adjust this if needed
                }));
                callback(attributes);
            }
        });
    } else {
        // Default: fetch standard metadata
        frappe.call({
            method: "lens_cpq.cpq.doctype.condition_type.api.get_meta_data", // server-side api method to call
            args: {
                doctype: frm.doc.document_reference
            },
            callback: function(response) {
                callback(response.message);
            }
        });
    }
}


// Generic function to populate field options for child tables
function fnPopulateFieldOptions(frm, iTableName, iFieldName) {
    // Get all field_name values already present in the child table to avoid duplicates
    const laCurrentRows = frm.doc[iTableName];
    //make an array only with label from the array of dict
    const laExistingLabels = laCurrentRows.map(idRow => idRow.field_name);
    
    //array to store excluded labels from already present in child table rows
    const laOptions = [];

    // Get metadata and filter out already used fields
    fnGetMetaData(frm, (iaMetaFields) => {
        iaMetaFields.forEach(field => {
            // if (!laExistingLabels.includes(field.label)) {
                laOptions.push(field.label);
            // }
        });

        // Update the child table's 'field_name' select options
        frm.fields_dict[iTableName].grid.update_docfield_property(
            iFieldName,      // The field inside child table (usually 'field_name')
            'options',     // Property to update
            laOptions // List of options to set
        );
    });
}

// Generic function to set the field type based on selected field name
function fnSetFieldTypeFromLabel(frm, cdt, cdn) {
    //get the rows data
    const idRow = locals[cdt][cdn];
    fnGetMetaData(frm, (idMetaFields) => {
        //get the fieldtype for the value selected in the field_name
        const ldMatched = idMetaFields.find(idField => idField.label === idRow.field_name);
        if (ldMatched) {
            // Set the field_type in the child row
            frappe.model.set_value(cdt, cdn, 'field_type', ldMatched.fieldtype);
        }
    });
}

// Input Sequence handlers
frappe.ui.form.on('Input Sequence', {
    input_sequence_add(frm, cdt, cdn) {
        // Populate options when a new row is added
        fnPopulateFieldOptions(frm, 'input_sequence', 'field_name');
    },
    field_name(frm, cdt, cdn) {
        // Set field_type when a field_name is selected
        fnSetFieldTypeFromLabel(frm, cdt, cdn);
    }
});

// Output Sequence handlers
frappe.ui.form.on('Output Sequence', {
    output_sequence_add(frm, cdt, cdn) {
        // Populate options when a new row is added
        fnPopulateFieldOptions(frm, 'output_sequence', 'field_name');
    },
    field_name(frm, cdt, cdn) {
        // Set field_type when a field_name is selected
        fnSetFieldTypeFromLabel(frm, cdt, cdn);
    }
});
