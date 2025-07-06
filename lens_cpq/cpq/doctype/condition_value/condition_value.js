// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Condition Value", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Condition Value', {
    // Triggered when the 'condition_type' field changes
    condition_type(frm) {
        // Fetch the selected 'Condition Type' document
        fnFetchConditionType(frm.doc.condition_type).then(conditionType => {
            // Transform the input sequence into the desired format: an array of objects containing field names
            const laInputValues = fnFormater(conditionType.input_sequence);
            // Similarly, transform the output sequence into the desired format: an array of objects containing field names
            const laOutputValues = fnFormater(conditionType.output_sequence);
            
            // Set the formatted input values into the 'input_condition_value' field on the form
            frm.set_value('input_condition_value', laInputValues);
            // Set the formatted output values into the 'output_condition_value' field on the form
            frm.set_value('output_condition_value', laOutputValues);

            frm.refresh_field('input_condition_value'); //Refresh the 'input_condition_value' field
            frm.refresh_field('output_condition_value'); // Refresh the 'output_condition_value' field 

            // Create an access key by joining all input_sequence's field names with a '/' separator
            const accessKey = conditionType.input_sequence.map(idField => idField.field_name).join('/');
            // Set the access key into the form field 'access_key'
            frm.set_value('access_key', accessKey);
        });
    },

// This event is triggered before the document is saved 
    validate(frm) {
        console.log(frm.doc.condition_type)
        // Fetch the condition type again to access the latest data for validation
        fnFetchConditionType(frm.doc.condition_type).then(conditionType => {
            console.log(conditionType)
            // Format the input values according to the sequence and set the final value in 'input_value' field
            const lInput = fnFormatFinalValue(
                conditionType.input_sequence,
                frm.doc.input_condition_value
            );
            // Format the output values according to the sequence and set the final value in 'output_value' field
            const lOutput = fnFormatFinalValue(
                conditionType.output_sequence,
                frm.doc.output_condition_value
            );

            frm.set_value('input_value', lInput);
            frm.set_value('output_value', lOutput);
        });
    }
});

// Fetches the 'Condition Type' document based on its name (iName)
function fnFetchConditionType(iName) {
    // Perform an asynchronous Frappe call to fetch the document by its name
    return new Promise((resolve) => {
        frappe.call({
            method: "frappe.client.get",
            args: { doctype: "Condition Type", name: iName },
            callback: (response) => resolve(response.message || {}) // When the call succeeds, resolve the promise with the document's data
        });
    });
}

// Transforms the sequence (input or output) into an array of objects containing only 'field_name' from each sequence item
function fnFormater(iaSequence = []) {
    // Map through the sequence array and return an array of objects with field_name
    return iaSequence.map(idSequence => ({
        field_name: idSequence.field_name // Extract only the 'field_name' from each sequence item
    }));
}

// Formats a field's value based on its length and type
function fnFormatFieldValue(iValue, iLength, iType) {
    // Convert the value to string and trim spaces at both ends
    let lValue = (iValue || '').toString().trim();
    
     // If the value is longer than the allowed length, truncate it
    if (lValue.length > iLength) {
        lValue = lValue.substring(0, iLength);
    }

    // Define an array of numeric types that require padding at the start
    const isNumeric = ['int', 'float', 'currency'].includes((iType || '').toLowerCase());
     // If the type is numeric, pad the value at the start with spaces, else pad at the end
    return isNumeric ? lValue.padStart(iLength, ' ') : lValue.padEnd(iLength, ' ');
}

// Formats the input or output values by matching them with the sequence order and applying formatting
function fnFormatFinalValue(iaSequence = [], iaValues = []) {
    const ldValueMap = {}; // Initialize an empty map to store values by field_name
    
    // Iterate over all the input/output condition values and map them by 'field_name'
    (iaValues || []).forEach(idRow => {
        ldValueMap[idRow.field_name] = idRow;
    });

    // Format the values in the order defined by the sequence and apply the necessary formatting
    return iaSequence.map(idSeq => {
        const ldRow = ldValueMap[idSeq.field_name];
         // If the value exists in the map, format it, otherwise return an empty string
        return ldRow ? fnFormatFieldValue(ldRow.value, idSeq.length, idSeq.field_type) : '';
    }).join(''); // Join all formatted values into a single string
}
