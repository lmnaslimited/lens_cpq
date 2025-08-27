// Copyright (c) 2025, LMNAs and contributors
// For license information, please see license.txt

frappe.ui.form.on("Chart of Design", {
    refresh(frm) {
        // Show "Convert to Group" for child node which is non numeric attribute
        if (!frm.doc.increment && !frm.doc.is_group == 1) {
            frm.add_custom_button(__('Convert to Group'), function () {
                frm.set_value('is_group', 1);
                frm.save();
            }, __("Actions"));
        }

        // Show "Convert to Child" only if group and has no children
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


        if (frm.doc.increment == 0 && frm.doc.item_attribute_value.length > 0) {

            let childTableWrapper = frm.fields_dict.item_attribute_value.grid.wrapper

            childTableWrapper.find(".grid-add-row").hide();

            childTableWrapper.find(".grid-remove-rows").hide();

            frm.fields_dict.item_attribute_value.grid.grid_rows.forEach(row => {

                if (row.doc.exclude == 1) {
                    $(row.row).css('background-color', '#FFF3CD');
                }
                else {
                    $(row.row).css('background-color', '');
                }
            });

            let attribute_values = frm.doc.item_attribute_value
                .filter(values => values.exclude == 0)
                .map(values => values.attribute_value);

            const selectTemplate = `
                    <div class="frappe-control input-max-width" data-fieldtype="Select" data-fieldname="default">
                        <div class="form-group">
                            <div class="clearfix">
                                <label class="control-label">Default Option</label>
                                <span class="help"></span>
                            </div>
                            <div class="control-input-wrapper">
                                <div class="control-input flex align-center">
                                    <select class="input-with-feedback form-control ellipsis" 
                                        data-fieldtype="Select" data-fieldname="default">
                                        {% for(var i = 0; i < values.length; i++) { %}
                                            <option value="{%= values[i] %}">{%= values[i] %}</option>
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
                        <span class="tooltip-content">default_option</span>
                    </div>
                `;

            console.log(attribute_values)
            const renderedSelect = frappe.render_template(selectTemplate, { values: attribute_values });

            frm.set_df_property("default", "options", renderedSelect);
            frm.refresh_field("default");

        }
    },
});