// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

frappe.ui.form.on("Chart of Design", {
    refresh(frm) {
        // Show "Convert to Group" for child node and non-numeric attribute
        if (!frm.doc.increment && !frm.doc.is_group == 1) {
            frm.add_custom_button(__('Convert to Group'), function () {
                frm.set_value('is_group', 1);
                frm.save();
            }, __("Actions"));
        }

        // Show "Convert to Child" for group node with no children
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

        // Render custom select for non-numeric attributes
        if (frm.doc.increment == 0 && frm.doc.attribute_value.length > 0) {

            // Hide add and remove buttons in child table
            let lChildTableWrapper = frm.fields_dict.attribute_value.grid.wrapper;

            lChildTableWrapper.find(".grid-add-row").hide();
            lChildTableWrapper.find(".grid-remove-rows").hide();

            // frm.set_df_property("attribute_value", cannot_add_rows, true);

            // Highlight excluded rows
            frm.fields_dict.attribute_value.grid.grid_rows.forEach(lRow => {
                if (lRow.doc.exclude == 1) {
                    $(lRow.row).css('background-color', '#f9d7d7ff');
                } else {
                    $(lRow.row).css('background-color', '');
                }
            });

            // Collect non-excluded attribute values
            let laAttributeValues = frm.doc.attribute_value
                .filter(lValues => lValues.exclude == 0)
                .map(lValues => lValues.attribute_value);

            // Custom select template
            const LSelectTemplate = `
                <div class="frappe-control input-max-width" data-fieldtype="Select" data-fieldname="non-numeric-default">
                    <div class="form-group">
                        <div class="clearfix">
                            <label class="control-label">Default</label>
                            <span class="help"></span>
                        </div>
                        <div class="control-input-wrapper">
                            <div class="control-input flex align-center">
                                <select class="input-with-feedback form-control ellipsis" 
                                    data-fieldtype="Select" data-fieldname="non-numeric-default">
                                    <option value=""></option>
                                    {% for(var i = 0; i < values.length; i++) { %}
                                        <option value="{%= values[i] %}" 
                                            {% if(values[i] == default_value) { %} selected {% } %}>
                                            {%= values[i] %}
                                        </option>
                                    {% } %}                                 
                                </select>
                                <div class="select-icon">
                                    <svg class="icon icon-sm" aria-hidden="true"><use href="#icon-select"></use></svg>
                                </div>
                            </div>
                            <div class="control-value like-disabled-input" style="display:none;"></div>
                            <p class="help-box small text-muted"></p>
                        </div>
                    </div>
                    <span class="tooltip-content">non-numeric-default</span>
                </div>
            `;

            // Render select with  non-excluded values
            const LRenderedSelect = frappe.render(LSelectTemplate, {
                values: laAttributeValues,
                default_value: frm.doc.default_value || ""
            });

            // Set custom select into default field
            frm.set_df_property("default", "options", LRenderedSelect);
            frm.refresh_field("default");

            // Update hidden default_value when selection changes (html field)
            frm.fields_dict.default.$wrapper
                .find('select[data-fieldname="non-numeric-default"]')
                .on("change", function () {
                    let lSelectedValue = $(this).val();
                    frm.set_value("default_value", lSelectedValue);
                });
        } else {
            // Render custom float input for numeric attributes
            const LFloatTemplate = `
            <div class="frappe-control input-max-width" data-fieldtype="Float" data-fieldname="numeric-default">
                <div class="form-group">
                    <div class="clearfix">
                        <label class="control-label" style="padding-right: 0px;">Default</label>
                        <span class="help"></span>
                    </div>
                    <div class="control-input-wrapper">
                        <div class="control-input">
                            <input type="text" autocomplete="off" 
                                class="input-with-feedback form-control" 
                                data-fieldtype="Float" data-fieldname="numeric-default" 
                                placeholder="" data-doctype="Chart of Design"
                                value="{%= value %}">
                        </div>
                        <div class="control-value like-disabled-input" style="display: none;"></div>
                        <p class="help-box small text-muted"></p>
                    </div>
                </div>
                <span class="tooltip-content">numeric-default</span>
            </div>
        `;

            // Render float template with current default value
            const LRenderedFloat = frappe.render(LFloatTemplate, { value: frm.doc.default_value || "" });

            // Set custom float into default field
            frm.set_df_property("default", "options", LRenderedFloat);
            frm.refresh_field("default");

            // Update hidden default_value on input change (html field)
            frm.fields_dict.default.$wrapper
                .find('input[data-fieldname="numeric-default"]')
                .on("input", function () {
                    let lSelectedValue = $(this).val();
                    frm.set_value("default_value", lSelectedValue);
                });
        }
    }
});
