# Copyright (c) 2025, LMNAs and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestDesign(FrappeTestCase):
    def test_duplicate_template_enabled_uses_template_name(self):
        frappe.get_doc({
        "doctype": "Item Attribute",
        "attribute_name": "High Voltage",
        "item_attribute_values": [
            {"attribute_value": "HV", "abbr": "HV"},

            ]
        }).insert()
        frappe.get_doc({
            "doctype": "Item Attribute",
            "attribute_name": "Power",
            "item_attribute_values": [
                {"attribute_value": "Rating", "abbr": "Rating"},
            ]
        }).insert()
        frappe.get_doc({
            "doctype": "Item Attribute",
            "attribute_name": "Power AN",
            "numeric_values": 1,
            "from_range": 100,
            "to_range": 25000,
            "increment": 1
        }).insert()
        frappe.get_doc({
            "doctype": "Item Attribute",
            "attribute_name": "HV",
            "numeric_values": 1,
            "from_range": 0,
            "to_range": 40,
            "increment": 0.1
        }).insert()
        self.design = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1,
            "template_name": "_Test OILT",
            "design_configurator":[
{'label': 'High Voltage - CR', 'is_group': 1, 'attribute': 'High Voltage', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"HV","abbr":"HV","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
{'label': 'Power - CR', 'is_group': 1, 'attribute': 'Power', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"Rating","abbr":"Rating","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
{'label': 'Power AN - CR', 'is_group': 0, 'attribute': 'Power AN', 'default_value': None, 'from_range': 100.0, 'to_range': 25000.0, 'increment': 1.0, 'options': '[]', 'parent_node': 'Power - CR', 'attribute_value': None},
{'label': 'HV - CR', 'is_group': 0, 'attribute': 'HV', 'default_value': None, 'from_range': 0.0, 'to_range': 40.0, 'increment': 0.1, 'options': '[]', 'parent_node': 'High Voltage - CR', 'attribute_value': None}
]
                                }).insert()

        self.assertEqual(self.design.name, "_Test OILT")

        duplicate = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1,
            "template_name": "_Test OILT",
            "design_configurator":[
{'label': 'High Voltage - CR', 'is_group': 1, 'attribute': 'High Voltage', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"HV","abbr":"HV","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
{'label': 'Power - CR', 'is_group': 1, 'attribute': 'Power', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"Rating","abbr":"Rating","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
{'label': 'Power AN - CR', 'is_group': 0, 'attribute': 'Power AN', 'default_value': None, 'from_range': 100.0, 'to_range': 25000.0, 'increment': 1.0, 'options': '[]', 'parent_node': 'Power - CR', 'attribute_value': None},
{'label': 'HV - CR', 'is_group': 0, 'attribute': 'HV', 'default_value': None, 'from_range': 0.0, 'to_range': 40.0, 'increment': 0.1, 'options': '[]', 'parent_node': 'High Voltage - CR', 'attribute_value': None}
]
                                })
        self.assertRaises(frappe.ValidationError, duplicate.insert)

        new_doc = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1,
        })
        self.assertRaises(frappe.ValidationError, new_doc.insert)

    def test_tree_rendering_api_returns_correct_tree_data(self):
        # ---------- Expected Output ----------
        expected_output = [
            {
                "value": "High Voltage - CR",
                "expandable": 1,
                "parent_id": "RGB",
                "attribute": "High Voltage",
                "doctype": "Design Configurator",
                
                "from_range": 0.0,
                "to_range": 0.0,
                "increment": 0.0,
                "default_value": None,
                "options": '[{"attribute_value":"HV","abbr":"HV","exclude":0}]'
            },
            {
                "value": "Power - CR",
                "expandable": 1,
                "parent_id": "RGB",
                "attribute": "Power",
                "doctype": "Design Configurator",
               
                "from_range": 0.0,
                "to_range": 0.0,
                "increment": 0.0,
                "default_value": None,
                "options": '[{"attribute_value":"Rating","abbr":"Rating","exclude":0}]'
            }
        ]
        # ---------- Actual Output From API ----------
        actual_output = frappe.call(
            "lens_cpq.cpq.doctype.design.api.get_children",
            doctype = "Design",
			parent= "RGB",
			parent_id= "_Test OILT"
        )

        # ---------- Compare both ----------
        self.assertCountEqual(
            actual_output,
            expected_output,
            "Tree Rendering API output does not match expected data!"
        )