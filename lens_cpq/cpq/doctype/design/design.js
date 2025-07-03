let InvalidValue = new Set()
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
        if (InvalidValue && InvalidValue.size > 0) {
            frappe.throw(__('Please correct all validation errors before saving.'));
        }
    },

    fnFetchAndRenderTemplateFields(frm) {
        frappe.call({
            method: "lens_cpq.cpq.doctype.design.api.fn_get_formated_item_variants",
            args: { item_name: frm.doc.design_template },
            callback: function (ldResponse) {
                if (!ldResponse.message) return;
                console.log("message", ldResponse.message)
                const LaFields = frm.events.fnMapFieldswithValues(frm, ldResponse.message);
                console.log("LaFields", LaFields)
                const LrenderHtml = frappe.render(frm.events.fnGenerateTemplateHtml(), { LaFields });
                console.log("LrenderHtml", LrenderHtml)
                frm.events.fnRenderDynamicSlider(frm, LrenderHtml, LaFields);
            }
        });
    },
    fnMapFieldswithValues(frm, iaFields) {
        return iaFields.map(ldField => ({
            ...ldField,
            lSavedValue: frm.events.fnMappingSavedValues(frm, ldField.fieldname)
                || ldField.default || ldField.min || ""
        }));
    },
    fnMappingSavedValues(frm, fieldname) {
        const laValues = (frm.doc.design_attributes || []).find(
            ldValue => ldValue.attribute.toLowerCase() === fieldname.toLowerCase()
        );
        return laValues ? laValues.attribute_value : null;
    },
    fnGenerateTemplateHtml() {
        return `
            <div class="design-grid-wrapper" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; column-gap: 24px;"> 
                {% for (var i = 0; i < LaFields.length; i++) {
                    var field = LaFields[i];
                %}
                <div class="form-column">
                    <div class="frappe-control input-max-width" data-fieldname="{%= field.fieldname %}">
                        <div class="form-group" style="margin-bottom: 6px;">
                            <label class="control-label" style="margin-bottom: 4px;">{%= field.label %}</label>
                            <div class="control-input flex flex-column" style="gap:6px;">
                                {% if (field.numeric_values) { %}
                                    <input type="range"
                                        class="range-field"
                                        data-fieldname="{%= field.fieldname %}"
                                        min="{%= field.min %}"
                                        max="{%= field.max %}"
                                        step="{%= field.step %}"
                                        value="{%= field.lSavedValue %}" 
                                        style="width: 100%; accent-color: black;" />

                                    <input type="number"
                                        class="number-field input-with-feedback form-control ellipsis"
                                        data-fieldname="{%= field.fieldname %}"
                                        min="{%= field.min %}"
                                        max="{%= field.max %}"
                                        step="{%= field.step %}"
                                        value="{%= field.lSavedValue %}"
                                        style="background-color: #F3F3F3; border-radius: 6px; padding: 6px;" />

                                    <small id="error_{%= field.fieldname %}" class="text-danger" style="margin-top: -4px;"></small>
                                    <small class="text-muted">
                                        From Range: {%= field.min %}, To Range: {%= field.max %}, Increment: {%= field.step %}
                                    </small>
                                {% } else { %}
                                    <select class="select-field form-control input-with-feedback ellipsis"
                                            data-fieldname="{%= field.fieldname %}"
                                            style="background-color: #F3F3F3; border-radius: 6px; padding: padding: revert-layer;">
                                        <option disabled {%= !field.lSavedValue ? 'selected' : '' %}>Select {%= field.label %}</option>
                                        {% for (var j = 0; j < field.options.length; j++) {
                                            var opt = field.options[j];
                                        %}
                                            <option value="{%= opt.value %}" {%= opt.value == field.lSavedValue ? 'selected' : '' %}>
                                                {%= opt.label %}
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
        console.log("");
        frm.set_df_property("dynamic_fields", "options", iRenderHtml);
           if (!document.getElementById("custom-slider-style")) {
            const css = `
                .range-field {
                    -webkit-appearance: none;
                    width: 100%;
                    height: 5px;
                    background: #ccc;
                    border-radius: 4px;
                    outline: none;
                    margin-top: 6px;
                }
                .range-field::-webkit-slider-thumb,
                .range-field::-moz-range-thumb {
                    border-radius: 8%;
                    background: black;
                    cursor: pointer;
                }
            `;
            $("<style id='custom-slider-style'>").text(css).appendTo("head");
        }
        frappe.after_ajax(() => {
            const $wrapper = $(frm.fields_dict["dynamic_fields"].$wrapper.get(0));

            iaFields.forEach(field => {
                const { fieldname, numeric_values } = field;

                if (numeric_values) {
                    const $range = $wrapper.find(`.range-field[data-fieldname="${fieldname}"]`);
                    const $number = $wrapper.find(`.number-field[data-fieldname="${fieldname}"]`);
                    const $error = $number.next('.text-danger');

                    const syncFields = ($src, $target) => {
                        const value = parseFloat($src.val());
                        const isValid = frm.events.fnValidateAndUpdateNumericInput(
                            frm, fieldname, value, $src.get(0), $target.get(0), $error.get(0)
                        );
                        if (isValid) $target.val(value);
                    };

                    $number.on("input", () => syncFields($number, $range));
                    $range.on("input", () => syncFields($range, $number));
                } else {
                    $wrapper.find(`.select-field[data-fieldname="${fieldname}"]`)
                        .on("change", function () {
                            frm.events.fnUpdateDesignAttribute(frm, fieldname, this.value);
                        });
                }
            });
        });
    },
    fnUpdateDesignAttribute(frm, fieldname, value) {
        let laRows = (frm.doc.design_attributes || []).find(
            ldRow => ldRow.attribute.toLowerCase() === fieldname.toLowerCase()
        );
        if (!laRows) {
            laRows = frm.add_child('design_attributes', { attribute: fieldname });
        }
        frappe.model.set_value(laRows.doctype, laRows.name, 'attribute_value', value);
    },
    fnValidateAndUpdateNumericInput(frm, fieldname, value, sourceElement, targetElement, errorEl) {
        const min = parseFloat(sourceElement.getAttribute("min"));
        const max = parseFloat(sourceElement.getAttribute("max"));
        const step = parseFloat(sourceElement.getAttribute("step"));
        let errorMessage = "";

        if (isNaN(value)) {
            errorMessage = __("Value is required");
        } else if (value < min || value > max) {
            errorMessage = __(`Value must be between ${min} and ${max}`);
        } else if (Math.abs(((value - min) / step) % 1) > 1e-6) {
            errorMessage = __(`Value should increment by ${step}`);
        }

        if (errorMessage) {
            errorEl.innerText = errorMessage;
            InvalidValue.add(fieldname);
            return false;
        }

        errorEl.innerText = "";
        targetElement.value = value;
        InvalidValue.delete(fieldname);
        frm.events.fnUpdateDesignAttribute(frm, fieldname, value);
        return true;
    }

});












