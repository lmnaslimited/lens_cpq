let lInvalidValue = new Set()
frappe.ui.form.on('Design', {
    refresh(frm) {
        if (frm.doc.design_template) {
            frm.events.fnFetchAndRenderTemplateFields(frm);
        }
    },

    design_template(frm) {
        frm.events.fnFetchAndRenderTemplateFields(frm);
    },

    validate(frm) {
        if (lInvalidValue && lInvalidValue.size > 0) {
            frappe.throw(__('Please correct all validation errors before saving.'));
        }
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
            }
        });
    },

    // Maps each field with its saved value or fallback to default/min
    fnMapFieldswithValues(frm, iaFields) {
        return iaFields.map(ldField => ({
            ...ldField,
            lSavedValue: frm.events.fnMappingSavedValues(frm, ldField.fieldname)
                || ldField.default || ldField.min || ""
        }));
    },

    // Gets the saved value of a specific attribute from the child table
    fnMappingSavedValues(frm, fieldname) {
        const ldValues = (frm.doc.design_attributes || []).find(
            ldValue => ldValue.attribute.toLowerCase() === fieldname.toLowerCase()
        );
        return ldValues ? ldValues.attribute_value : null;
    },
    
    // Defines the HTML structure for dynamic field rendering
    fnGenerateTemplateHtml() {
        return `
            <style id="custom-slider-style">
                .range-field {
                    -webkit-appearance: none; width: 100%; height: 5px;
                    background: #ccc; border-radius: 4px; outline: none; margin-top: 6px;
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
                                        <option disabled {%= !ldField.lSavedValue ? 'selected' : '' %}>Select {%= ldField.label %}</option>
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
                const { fieldname, numeric_values } = ldField;
                const LescapedFieldname = CSS.escape(ldField.fieldname);
                if (numeric_values) {
                    const $elRange = $elDynamicWrapper.find(`.range-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elNumber = $elDynamicWrapper.find(`.number-field[data-fieldname="${LescapedFieldname}"]`);
                    const $elError = $elNumber.next('.text-danger');

                    const fnsyncFields = ($elSrc, $elTarget) => {
                        const lValue = parseFloat($elSrc.val());
                        const lIsValid = frm.events.fnValidateAndUpdateNumericInput(
                            frm, fieldname, lValue, $elSrc.get(0), $elTarget.get(0), $elError.get(0)
                        );
                        if (lIsValid) $elTarget.val(lValue);
                    };

                    $elNumber.on("input", () => fnsyncFields($elNumber, $elRange));
                    $elRange.on("input", () => fnsyncFields($elRange, $elNumber));
                } else {
                    
                    $elDynamicWrapper.find(`.select-field[data-fieldname="${LescapedFieldname}"]`)
                        .on("change", function () {
                            frm.events.fnUpdateDesignAttribute(frm, fieldname, this.value);
                        });
                }
            });
        });
    },

     // Updates the design_attributes child table with the selected value
    fnUpdateDesignAttribute(frm, iFieldname, iValue) {
        let laRows = (frm.doc.design_attributes || []).find(
            ldRow => ldRow.attribute.toLowerCase() === iFieldname.toLowerCase()
        );
        if (!laRows) {
            laRows = frm.add_child('design_attributes', { attribute: iFieldname });
        }
        frappe.model.set_value(laRows.doctype, laRows.name, 'attribute_value', iValue);
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
        } else if (Math.abs(((iValue - lMin) / lStep) % 1) > 1e-6) {
            lErrorMessage = __(`Value should increment by ${lStep}`);
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












