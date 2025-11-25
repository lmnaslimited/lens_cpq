import frappe
from frappe import _

@frappe.whitelist()
def fn_get_formated_item_variants(item_name):
    """
    Fetches and formats the attributes for a given item.

    This API retrieves attributes associated with an item and returns them as a structured list. 
    Each attribute is represented as a field configuration, specifying whether it is a range-based 
    field or a select-type field. The configuration includes default values, options, and range specifications where applicable.

    Parameters:
        item_name (str): The name of the item for which attributes need to be fetched.

    Returns:
        list[dict]: A list of dictionaries representing attribute field configurations. 
        Each dictionary includes:
            - label, name ,type ,numeric_values ,min ,max ,step ,default ,options 

    Raises:
        DoesNotExistError: If the specified item does not exist.
        Exception: If any other error occurs, the error is logged and a user-friendly message is thrown.
    """
    la_item = frappe.get_all(
        "Item", 
        filters={"item_code":item_name}, 
        fields=[
            "`tabItem Variant Attribute`.attribute",
            "`tabItem Variant Attribute`.attribute_value",
            "`tabItem Variant Attribute`.numeric_values",
            "`tabItem Variant Attribute`.from_range",
            "`tabItem Variant Attribute`.increment",
            "`tabItem Variant Attribute`.to_range",
        ],
        order_by="`tabItem Variant Attribute`.idx"
        )
        
    la_non_numeric = [ld_record.attribute for ld_record in la_item if not ld_record.numeric_values]
    ld_non_numeric_options_map = {}
    if la_non_numeric:
        la_attribute_values = frappe.get_all(
            "Item Attribute Value",
            filters={"parent": ["in", la_non_numeric]},
            fields=["parent", "attribute_value"],
            order_by="idx ASC"
        )
        for ld_value in la_attribute_values:
            #setdefault is a python build in method for grouping
            ld_non_numeric_options_map.setdefault(ld_value.parent, []).append({
                "label": ld_value.attribute_value,
                "value": ld_value.attribute_value
            })
            
    la_fields = []

    for ld_attribute in la_item:
        if ld_attribute.numeric_values:
            ld_field = {
                "label": ld_attribute.attribute,
                "fieldname": ld_attribute.attribute.replace(" ", "_").lower(),
                "fieldtype": "range",
                "numeric_values": 1,
                "min": ld_attribute.from_range,
                "max": ld_attribute.to_range,
                "step": ld_attribute.increment,
                "from_range": ld_attribute.from_range,
                "to_range": ld_attribute.to_range,
                "increment": ld_attribute.increment,
                "default": ld_attribute.attribute_value
            }
        else:
            ld_field = {
                "label": ld_attribute.attribute,
                "fieldname": ld_attribute.attribute.replace(" ", "_").lower(),
                "fieldtype": "select",
                "numeric_values": 0,
                "default": ld_attribute.attribute_value,
                "from_range": ld_attribute.from_range,
                "to_range": ld_attribute.to_range,
                "increment": ld_attribute.increment,
                "options": ld_non_numeric_options_map[ld_attribute.attribute]
            }
        la_fields.append(ld_field)


    return la_fields

@frappe.whitelist()
def fn_create_item_from_design(design_name):
    """
    Creates a new item variant based on the details from the specified design document. 
    This function uses the design template to fetch the item template and associated attributes, 
    creates a new item variant, and updates it with the relevant attributes from the design document. 
    It also creates a standard selling price for the new item based on the design's total cost.

    Parameters:
    - design_name (str): The name of the design document to fetch the item details from.

    Returns:
    - str: The item code of the newly created item variant.
    
    Raises:
    - frappe.exceptions.ValidationError: If the design template is not specified in the design document.
    """

    #get the details of the design
    ld_design_doc = frappe.get_doc("Design", design_name)

    if not ld_design_doc.design_template:
        frappe.throw(__('Design Template is not specified in the design document.'))

    #get the details of the item template
    ld_template_item = frappe.get_doc("Item", ld_design_doc.design_template)

    #Forming a dictionary with key as variant's name and value as is_numeric
    ld_template_attributes = {
        attr.attribute: attr.numeric_values for attr in ld_template_item.attributes
    }

    #replacing space with - for item name and code formation
    la_attribute_values = [
        attribute.attribute_value.replace(" ", "-")
        for attribute in ld_design_doc.design_attributes
        if attribute.attribute in ld_template_attributes
    ]
    l_item_code = f"{ld_design_doc.design_template}-" + "-".join(la_attribute_values)

    ld_item_variant = frappe.new_doc("Item")
    ld_item_variant.item_code = l_item_code
    ld_item_variant.item_name = l_item_code
    ld_item_variant.item_group = ld_template_item.item_group
    ld_item_variant.is_stock_item = ld_template_item.is_stock_item
    ld_item_variant.variant_of = ld_design_doc.design_template
    ld_item_variant.stock_uom = ld_template_item.stock_uom
    ld_item_variant.include_item_in_manufacturing = 0
    ld_item_variant.custom_design = ld_design_doc.name

    for ld_attribute in ld_design_doc.design_attributes:
        if ld_attribute.attribute in ld_template_attributes:

            l_numeric_value = ld_template_attributes[ld_attribute.attribute]
            
            ld_item_variant.append("attributes", {
                "attribute": ld_attribute.attribute,
                "attribute_value": ld_attribute.attribute_value,
                "numeric_values": l_numeric_value
            })

    ld_item_variant.insert()
    # frappe.db.commit()

    # # Create a "Standard Selling" price list for this item
    # ld_item_price = frappe.new_doc("Item Price")
    # ld_item_price.item_code = ld_item_variant.item_code
    # ld_item_price.price_list = "Standard Selling"
    # ld_item_price.price_list_rate = ld_design_doc.total_cost
    # ld_item_price.insert()
    return ld_item_variant.item_code

@frappe.whitelist()
def get_children(doctype=None, parent=None, **kwargs):
    if isinstance(kwargs, str):
        kwargs = frappe.parse_json(kwargs)

    if isinstance(kwargs, dict):
        kwargs = frappe._dict(kwargs)

    fields = [
        "label as value",
        "is_group as expandable",
        "parent_node as parent_id",
        "attribute",
        "'Design Configurator' as doctype",
        "from_range",
        "to_range",
        "increment",
        "default_value",
        "options",
    ]

    query_filters = {
        "parent": kwargs.parent_id,
    }

    la_config_items = frappe.get_all(
        "Design Configurator",
        fields=fields,
        filters=query_filters,
        order_by="idx"
    )

    # print("get all", la_config_items)

    return la_config_items

