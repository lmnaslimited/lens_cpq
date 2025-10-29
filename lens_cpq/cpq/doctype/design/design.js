let lInvalidValue = new Set()
let lIsUpdatingFields = false;
let ldFieldFilteredOptions = {};
frappe.ui.form.on('Design', {
    refresh(frm) {

        // Build tree only if not already loaded for this document
        if (!frappe.design_configurator || frappe.design_configurator.design_configurator !== frm.doc.name) {
            frm.trigger("build_tree");
        }

        if (frm.doc.design_template) {

            frm.events.fnFetchAndRenderTemplateFields(frm);

            // After refreshing the form, update the options based on the condition value 
            //not from the Item attributes
            frappe.after_ajax(() => {
                frappe.call({
                    method: "lens_cpq.cpq.doctype.condition_type.api.condition_type",
                    args: { doc: frm.doc },
                    callback: function (ldResponse) {
                        if (!ldResponse.message) return;

                        const LaConditionResults = ldResponse.message[0]?.target || [];

                        // Clear old filtered laOptions
                        ldFieldFilteredOptions = {};

                        LaConditionResults.forEach(ldResult => {
                            const LTargetField = ldResult.fieldName;
                            // const LTargetValue = ldResult.value;
                            const laOptions = ldResult.options || [];

                            // Save for use in fnMapFieldswithValues
                            ldFieldFilteredOptions[LTargetField.replace(/ /g, "_").toLowerCase()] = laOptions.map(opt => ({
                                label: opt,
                                value: opt
                            }));

                            // Also update the child table (optional if needed)
                            let ldTargetRow = (frm.doc.design_attributes || []).find(
                                ldRow => ldRow.attribute.toLowerCase() === LTargetField.toLowerCase()
                            );

                            if (!ldTargetRow) {
                                ldTargetRow = frm.add_child('design_attributes', {
                                    attribute: LTargetField
                                });
                            }
                            // frappe.model.set_value(ldTargetRow.doctype, ldTargetRow.name, 'attribute_value', LTargetValue);
                        });
                        // Re-render fields using updated options
                        frm.events.fnFetchAndRenderTemplateFields(frm);
                    }
                });
            });
        }
        if (frm.doc.item) {
            frm.add_custom_button(__("View Item"), function () {
                frappe.set_route("item", frm.doc.item)
            })
        } else {
            frm.add_custom_button(__("Create Item"), function () {
                frappe.call({
                    method: "lens_cpq.cpq.doctype.design.api.fn_create_item_from_design",
                    args: {
                        design_name: frm.doc.name
                    },
                    callback: function (ldResponse) {
                        if (ldResponse.message) {
                            frm.set_value("item", ldResponse.message)
                            frm.save()
                        }
                        frappe.show_alert("Item is Successfully Created", 5)
                    }
                })
            })
        }
    },

    validate(frm) {
        if (lInvalidValue && lInvalidValue.size > 0) {
            frappe.throw(__('Please correct all validation errors before saving.'));
        }
    },

    design_template(frm) {
        frm.events.fnFetchAndRenderTemplateFields(frm);
    },

    build_tree(frm) {

        // Select the wrapper div of the 'design_tree' HTML field
        let lParent = $(frm.fields_dict["design_tree"].wrapper);

        // Clear old tree content
        lParent.empty();

        // Load design configurator bundle and render tree
        frappe.require("design_configurator.bundle.js").then(() => {
            frappe.design_configurator = new frappe.ui.DesignConfigurator({
                wrapper: lParent,
                page: lParent,
                frm: frm,
                design_configurator: frm.doc.name,
            });
        });
    },

    // Fetches field data from the server and renders the input fields
    fnFetchAndRenderTemplateFields(frm) {
        frappe.call({
            method: "lens_cpq.cpq.doctype.design.api.fn_get_formated_item_variants",
            args: { item_name: frm.doc.design_template },
            callback: function (ldResponse) {
                if (!ldResponse.message) return;
                const LaFields = frm.events.fnMapFieldswithValues(frm, ldResponse.message);
                const LrenderHtml = frappe.render(frm.events.fnGenerateTemplateHtml(), { LaFields });
                frm.events.fnRenderDynamicSlider(frm, LrenderHtml, LaFields);
                (LaFields || []).forEach(ldField => {
                    const lValue = ldField.lSavedValue;
                    const lName = ldField.label || ldField.fieldname;
                    let ldRow = (frm.doc.design_attributes || []).find(
                        row => row.attribute.toLowerCase() === lName.toLowerCase()
                    );
                    if (!ldRow) {
                        ldRow = frm.add_child('design_attributes', {
                            attribute: lName,
                            attribute_value: lValue
                        });
                    } else if (!ldRow.attribute_value && lValue) {
                        frappe.model.set_value(ldRow.doctype, ldRow.name, 'attribute_value', lValue);
                    }
                });

                frm.refresh_field("design_attributes");
            }
        });
    },

    // Maps each field with its saved value or fallback to default/min
    fnMapFieldswithValues(frm, iaFields) {
        return iaFields.map(ldField => {
            const ldRow = (frm.doc.design_attributes || []).find(
                ldResponse => ldResponse.attribute.replace(/ /g, "_").toLowerCase() === ldField.fieldname
            );
            // const filteredOptions = ldFieldFilteredOptions[ldField.label] || [];
            const LaFilteredOptions = ldFieldFilteredOptions[ldField.fieldname.toLowerCase()] || [];
            return {
                ...ldField,
                lSavedValue: ldRow?.attribute_value ?? ldField.default ?? ldField.min ?? "",
                options: LaFilteredOptions.length > 0 ? LaFilteredOptions : ldField.options || []
            };
        });
    },

    // Defines the HTML structure for dynamic field rendering
    fnGenerateTemplateHtml() {
        return `
            <style id="custom-slider-style">
                .range-field {
                   width: 100%; height: 5px;
                   border-radius: 4px; outline: none; margin-top: 6px;
                }
                .range-field::-webkit-slider-thumb,
                .range-field::-moz-range-thumb {
                    border-radius: 8%; background: black; cursor: pointer;
                }
            </style>

            <div class="design-grid-wrapper" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; column-gap: 30px;"> 
                {% for (var laIndex = 0; laIndex < LaFields.length; laIndex++) {
                    var ldField = LaFields[laIndex];
                %}
                <div class="form-column">
                    <div class="frappe-control input-max-width" data-fieldname="{%= ldField.fieldname %}">
                        <div class="form-group" style="margin-bottom: 6px;">
                            <label class="control-label" style="margin-bottom: 4px;">{%= ldField.label %}</label>
                            <div class="control-input flex flex-column" style="gap:6px;">
                                {% if (ldField.numeric_values) { %}
                                    <input type="range"
                                        class="range-field"
                                        data-fieldname="{%= ldField.fieldname %}"
                                        min="{%= ldField.min %}"
                                        max="{%= ldField.max %}"
                                        step="{%= ldField.step %}"
                                        value="{%= ldField.lSavedValue %}" 
                                        style="width: 100%; accent-color: black;" />

                                    <input type="number"
                                        class="number-field input-with-feedback form-control ellipsis"
                                        data-fieldname="{%= ldField.fieldname %}"
                                        min="{%= ldField.min %}"
                                        max="{%= ldField.max %}"
                                        step="{%= ldField.step %}"
                                        value="{%= ldField.lSavedValue %}"
                                        style="background-color: #F3F3F3; border-radius: 6px; padding: 6px;" />

                                    <small id="error_{%= ldField.fieldname %}" class="text-danger" style="margin-top: -4px;"></small>
                                    <small class="text-muted">
                                        From Range: {%= ldField.min %}, To Range: {%= ldField.max %}, Increment: {%= ldField.step %}
                                    </small>
                                {% } else { %}
                                    <select class="select-field form-control input-with-feedback ellipsis"
                                            data-fieldname="{%= ldField.fieldname %}"
                                            style="background-color: #F3F3F3; border-radius: 6px; padding: padding: revert-layer;">
                                        <option disabled {%= !ldField.lSavedValue ? 'selected' : '' %}></option>
                                        {% for (var laOption = 0; laOption < ldField.options.length; laOption++) {
                                            var ldOpt = ldField.options[laOption];
                                        %}
                                            <option value="{%= ldOpt.value %}" {%= ldOpt.value == ldField.lSavedValue ? 'selected' : '' %}>
                                                {%= ldOpt.label %}
                                            </option>
                                        {% } %}
                                    </select>
                                {% } %}
                            </div>
                        </div>
                    </div>
                </div>
                {% } %}
            </div>
        `;
    },

    fnRenderDynamicSlider(frm, iRenderHtml, iaFields) {
        frm.set_df_property("dynamic_fields", "options", iRenderHtml);
        frappe.after_ajax(() => {
            const $elDynamicWrapper = $(frm.fields_dict["dynamic_fields"].$wrapper.get(0));
            iaFields.forEach(ldField => {
                const { fieldname, numeric_values, label } = ldField;
                const LescapedFieldname = CSS.escape(fieldname);
                if (numeric_values) {
                    //we are using the same logic bellow for condition too
                    const $elRange = $elDynamicWrapper.find(`.range-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elNumber = $elDynamicWrapper.find(`.number-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elError = $elNumber.next('.text-danger');

                    const fnsyncFields = ($elSrc, $elTarget) => {
                        const lValue = parseFloat($elSrc.val());
                        const lIsValid = frm.events.fnValidateAndUpdateNumericInput(
                            frm, label, lValue, $elSrc.get(0), $elTarget.get(0), $elError.get(0)
                        );
                        if (lIsValid) $elTarget.val(lValue);
                    };

                    $elNumber.on("input", () => fnsyncFields($elNumber, $elRange));
                    $elRange.on("input", () => fnsyncFields($elRange, $elNumber));
                } else {

                    $elDynamicWrapper.find(`.select-field[data-fieldname="${LescapedFieldname}"]`)
                        .on("change", function () {
                            frm.events.fnUpdateDesignAttribute(frm, label, this.value, ldField);
                        });
                }
            });
        });
    },

    fnUpdateDesignAttribute(frm, iFieldname, iValue, fields = []) {
        if (lIsUpdatingFields) return;
        lIsUpdatingFields = true;
        // Step 1: Update or add the current attribute to the child table
        let ldRow = (frm.doc.design_attributes || []).find(
            ldResponse => ldResponse.attribute.toLowerCase() === iFieldname.toLowerCase()
        );

        if (!ldRow) {
            ldRow = frm.add_child('design_attributes', { attribute: iFieldname });
        }

        frappe.model.set_value(ldRow.doctype, ldRow.name, 'attribute_value', iValue);

        // Step 2: Call backend to evaluate conditional logic
        frappe.call({
            method: "lens_cpq.cpq.doctype.condition_type.api.condition_type",
            args: { doc: frm.doc },
            callback: function (ldResponse) {
                if (!ldResponse.message) {
                    lIsUpdatingFields = false;
                    return;
                }

                const LaConditionResults = ldResponse.message[0]?.target || [];

                // Step 3: Apply all returned condition results to design_attributes and UI
                for (let ldResult of LaConditionResults) {

                    const LTargetField = ldResult.fieldName;
                    const LTargetValue = ldResult.value;
                    const laOptions = ldResult.options || [];

                    // Update or add the field in design_attributes child table
                    let ldTargetRow = (frm.doc.design_attributes || []).find(
                        ldRow => ldRow.attribute.toLowerCase() === LTargetField.toLowerCase()
                    );

                    if (!ldTargetRow) {
                        ldTargetRow = frm.add_child('design_attributes', {
                            attribute: LTargetField
                        });
                    }
                    if (LTargetValue) {
                        frappe.model.set_value(ldTargetRow.doctype, ldTargetRow.name, 'attribute_value', LTargetValue);
                    }

                    // ldFieldFilteredOptions[LTargetField] = laOptions.map(opt => ({
                    //     label: opt,
                    //     value: opt
                    // }));

                    ldFieldFilteredOptions[LTargetField.replace(/ /g, "_").toLowerCase()] = laOptions.map(iOpt => ({
                        label: iOpt,
                        value: iOpt
                    }));

                    // ✅ the fnRenderDynamicSlider logic is reused
                    const $wrapper = $(frm.fields_dict["dynamic_fields"].$wrapper.get(0));
                    const LescapedFieldname = CSS.escape(LTargetField.replaceAll(" ", "_").toLowerCase());
                    const $select = $wrapper.find(`.select-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elRange = $wrapper.find(`.range-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elNumber = $wrapper.find(`.number-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elError = $elNumber.next('.text-danger');


                    if ($select.length && laOptions.length > 0) {
                        fields.options = laOptions
                        $select.empty();
                        laOptions.forEach(opt => {
                            const $opt = $('<option>')
                                .val(opt)
                                .text(opt);
                            if (opt === LTargetValue) {
                                $opt.prop('selected', true);
                            }
                            $select.append($opt);
                        });
                    } else if ($elRange.length) {
                        const lValid = frm.events.fnValidateAndUpdateNumericInput(
                            frm, LTargetField, LTargetValue, $elRange.get(0), $elNumber.get(0), $elError.get(0)
                        );
                        if (lValid) $elRange.val(LTargetValue);

                    } else {
                        frm.events.fnFetchAndRenderTemplateFields(frm)
                    }

                }
                lIsUpdatingFields = false;
                frm.events.fnFetchAndRenderTemplateFields(frm)
            }
        });
    },

    // Validates the numeric input value and shows an error message if it is out of range
    // Removes the field from the error list if the value is valid
    fnValidateAndUpdateNumericInput(frm, iFieldname, iValue, elSourceElement, elTargetElement, elErrorElement) {
        const lMin = parseFloat(elSourceElement.getAttribute("min"));
        const lMax = parseFloat(elSourceElement.getAttribute("max"));
        const lStep = parseFloat(elSourceElement.getAttribute("step"));
        let lErrorMessage = "";

        if (isNaN(iValue)) {
            lErrorMessage = __("Value is required");
        } else if (iValue < lMin || iValue > lMax) {
            lErrorMessage = __(`Value must be between ${lMin} and ${lMax}`);
        } else {
            const lQuotient = (iValue - lMin) / lStep;
            const lIsStepValid = Math.abs(lQuotient - Math.round(lQuotient)) < 1e-6;
            if (!lIsStepValid) {
                lErrorMessage = __(`Value should increment by ${lStep}`);
            }
        }

        if (lErrorMessage) {
            elErrorElement.innerText = lErrorMessage;
            lInvalidValue.add(iFieldname);
            return false;
        }

        elErrorElement.innerText = "";
        elTargetElement.value = iValue;
        lInvalidValue.delete(iFieldname);
        frm.events.fnUpdateDesignAttribute(frm, iFieldname, iValue);
        return true;
    }
});