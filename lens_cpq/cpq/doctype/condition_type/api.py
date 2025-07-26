import frappe
from frappe import _

@frappe.whitelist()
def get_meta_data(doctype):
    id_meta = frappe.get_meta(doctype)

    return id_meta.fields

@frappe.whitelist()
def condition_type(doc):
    # Parse if coming as string
    if isinstance(doc, str):
        doc = frappe.parse_json(doc)

    # Get doc object
    ld_data = frappe.get_doc(doc)

    # Early exit: No condition types for this DocType
    if not frappe.db.exists('Condition Type', {'document_reference': ld_data.doctype}):
        return []

    # Get all condition types for this Doctype
    la_condition_types = frappe.get_list(
        'Condition Type',
        filters={'document_reference': ld_data.doctype}
    )

    la_result = []

    def fn_get_fieldname_from_label(doctype, label):
        """Get fieldname from label for a given DocType"""
        ld_meta = frappe.get_meta(doctype)
        for ld_field in ld_meta.fields:
            if ld_field.label == label:
                return ld_field.fieldname
        return None

    def fn_get_design_attribute(fieldname):
        """Helper to get attribute_value from design_attributes child table"""
        for ld_row in ld_data.design_attributes or []:
            if ld_row.attribute == fieldname:
                return ld_row.attribute_value
        return None
    #looping the condition type
    for ld_condition_type in la_condition_types:
        # geting the full document
        ld_condition_type_detail = frappe.get_doc('Condition Type', ld_condition_type.name)
        # if not enable leave the loop and start next loop
        if not ld_condition_type_detail.enable:
            continue
        # if its value based condition
        if ld_condition_type_detail.is_value_based:
            # get the input sequence child table
            la_input_sequence = ld_condition_type_detail.input_sequence
            # get the input sequence child table
            la_output_sequence = ld_condition_type_detail.output_sequence
            # get the relavent Condition Value
            ld_condition_value = frappe.get_doc('Condition Value', {'condition_type': ld_condition_type_detail.name})
            # here one contion type can have multiple condition value so we need to loop it here actually

            #get the access key from condition value
            l_access_key = ld_condition_value.access_key
            #get the input value from condition value
            la_input_value = ld_condition_value.input_value
            #get the output value from condition value
            la_output_value = ld_condition_value.output_value
            
            # here access key will have all ghe input fieldname separated by /
            la_source_labels = l_access_key.split('/')
            la_source_fields = []
            # for each field name
            for l_label in la_source_labels:
                # get the correct field name from metadat or from design if the doctype is design
                field_name = fn_get_fieldname_from_label(ld_data.doctype, l_label)
                # if not field_name and ld_data.doctype != "Design":
                #     field_name = fn_get_fieldname_from_label("Design", l_label)
                    # append the field name
                la_source_fields.append(field_name or l_label)
            # la_source_fields = [fn_get_fieldname_from_label(ld_doc.doctype, label) for label in la_source_labels]
            la_source_fields_value = []
            l_input_index = 0
            # again for each field name
            for l_field in la_source_labels:
                # for each condition type's input sequence
                # if the each row field name is equal to the looping field
                #return that row of the input sequence
                la_matching_rows = [row for row in la_input_sequence if row.field_name == l_field]
                
                if la_matching_rows:
                    # exract the length value from that row
                    l_row_length = la_matching_rows[0].length
                    # index and the fetched row's length is should be within or equal to input value of condition value (that is chara )       
                    if l_input_index + l_row_length <= len(la_input_value):
                        l_extracted_value = la_input_value[l_input_index:l_input_index + l_row_length]
                    else:
                        l_extracted_value = la_input_value[l_input_index:].strip()
                    
                    l_extracted_value = l_extracted_value.strip()
                    #now append the value
                    la_source_fields_value.append(l_extracted_value)
                    l_input_index += l_row_length
            #now combain both fieldname with its value
            la_source = [{field: value} for field, value in zip(la_source_fields, la_source_fields_value)]
            
            #check if the processing document has same value in the source field as the one maintain in condition value input value tabel
            if ld_data.doctype == "Design":
                l_source_conditions_met = all(
                    str(fn_get_design_attribute(field)) == str(value)
                    for field, value in zip(la_source_fields, la_source_fields_value) #they are key variable from zip
                )
            else:
                l_source_conditions_met = all(
                    str(ld_data.get(field)) == str(value)
                    for field, value in zip(la_source_fields, la_source_fields_value)
                )
            la_target = []
            if not l_source_conditions_met:
                # If condition not met, skip this condition type
                # Only clear fields with output_type 'Options'
                for ld_row in la_output_sequence:
                    l_matching_output_cond = next(
                        (cond for cond in ld_condition_value.output_condition_value
                        if cond.field_name == ld_row.field_name),
                        None
                    )
                    if l_matching_output_cond and l_matching_output_cond.output_type == "Options":
                        la_target.append({
                            "fieldName": ld_row.field_name,
                            # "value": '',
                            "options": []
                        })

                la_result.append({
                    "target": la_target
                })
                continue  # Move to next condition type

                        
                        
            l_output_index = 0
            # since we dont have cutshort method to find output field name like we do for input field name 
            # so we looping through condition type output sequence tabel
            for ld_row in la_output_sequence:
                #extract the length
                l_row_length = ld_row.length
                # index and the fetched row's length is should be within or equal to output value of condition value (that is chara )  
                if l_output_index + l_row_length <= len(la_output_value):
                    l_extracted_value = la_output_value[l_output_index:l_output_index + l_row_length]
                else:
                    l_extracted_value = la_output_value[l_output_index:].strip()

                l_extracted_value = l_extracted_value.strip()
                l_output_index += l_row_length

            
                l_label = ld_row.field_name
                if ld_data.doctype == "Design":
                    l_fieldname = l_label
                else:
                    l_fieldname = fn_get_fieldname_from_label(ld_data.doctype, l_label)

                if l_fieldname:
                    # Find matching condition row from output_condition_value
                    l_matching_output_cond = next(
                        (cond for cond in ld_condition_value.output_condition_value
                        if cond.field_name == l_label),
                        None
                    )

                    l_output_type = getattr(l_matching_output_cond, 'output_type', 'Single')
                    l_options_str = getattr(l_matching_output_cond, 'options', '')
                    l_default_value = getattr(l_matching_output_cond, 'default', '')

                    # if output_type == 'Options':
                    #     options = [opt.strip() for opt in (options_str or "").split(",") if opt.strip()]
                    #     value =  default_value if default_value else options[0]
                    #     ld_data.set(fieldname, value)
                    #     la_target.append({
                    #         "fieldName": fieldname,
                    #         "value": value,
                    #         "options": options
                    #     })
                    if l_output_type == 'Options':
                        la_options = [opt.strip() for opt in (l_options_str or "").split(",") if opt.strip()]
                        l_current_value = ld_data.get(l_fieldname)

                        if l_current_value in la_options:
                            l_value = l_current_value
                        else:
                            l_value = l_default_value if l_default_value else (la_options[0] if la_options else '')

                        ld_data.set(l_fieldname, l_value)
                        la_target.append({
                            "fieldName": l_fieldname,
                            "value": l_value,
                            "options": la_options
                        })

                    else:
                        l_value = l_extracted_value if l_extracted_value else (getattr(ld_row, 'default_value', '') or '')
                        ld_data.set(l_fieldname, l_value)
                        la_target.append({
                            "fieldName": l_fieldname,
                            "value": l_value
                        })

            # Append full source-target pair
            la_result.append({
                "source": la_source,
                "target": la_target
            })

        elif ld_condition_type_detail.is_api_based:
            pass
        
        elif ld_condition_type_detail.is_formula_based:
            pass
    
    return la_result