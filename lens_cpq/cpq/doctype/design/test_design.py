# Copyright (c) 2025, LMNAs and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase

class TestDesign(FrappeTestCase):
	def test_template_creation(self):
		self.ld_hign_voltage = frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "_Test High Voltage",
			"item_attribute_values": [{"attribute_value": "_Test HV", "abbr": "HV"}]
		}).insert()

		self.ld_power = frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "_Test Power",
			"item_attribute_values": [{"attribute_value": "_Test Rating", "abbr": "Rating"}]
		}).insert()

		self.ld_power_an = frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "_Test Power AN",
			"numeric_values": 1,
			"from_range": 100,
			"to_range": 25000,
			"increment": 1
		}).insert()

		self.ld_hv = frappe.get_doc({
			"doctype": "Item Attribute",
			"attribute_name": "_Test HV",
			"numeric_values": 1,
			"from_range": 0,
			"to_range": 40,
			"increment": 0.1
		}).insert()
		self.ld_design = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1,
            "template_name": "_Test OILTM",
            "design_configurator": [
                {'label': 'High Voltage - CR', 'is_group': 1, 'attribute': '_Test High Voltage', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"_Test HV","abbr":"HV","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
                {'label': 'Power - CR', 'is_group': 1, 'attribute': '_Test Power', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"_Test Rating","abbr":"Rating","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
                {'label': 'Power AN - CR', 'is_group': 0, 'attribute': '_Test Power AN', 'default_value': None, 'from_range': 100.0, 'to_range': 25000.0, 'increment': 1.0, 'options': '[]', 'parent_node': 'Power - CR', 'attribute_value': None},
                {'label': 'HV - CR', 'is_group': 0, 'attribute': '_Test HV', 'default_value': None, 'from_range': 0.0, 'to_range': 40.0, 'increment': 0.01, 'options': '[]', 'parent_node': 'High Voltage - CR', 'attribute_value': None}
                ]
        }).insert()
		self.assertEqual(self.ld_design.template_name, "_Test OILTM")

        # Testing Duplicate Scenario
		ld_duplicate = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1,
            "template_name": "_Test OILTM",
            "design_configurator":  [
                {'label': 'High Voltage - CR', 'is_group': 1, 'attribute': '_Test High Voltage', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"HV","abbr":"HV","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
                {'label': 'Power - CR', 'is_group': 1, 'attribute': '_Test Power', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"Rating","abbr":"Rating","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
                {'label': 'Power AN - CR', 'is_group': 0, 'attribute': '_Test Power AN', 'default_value': None, 'from_range': 100.0, 'to_range': 25000.0, 'increment': 1.0, 'options': '[]', 'parent_node': 'Power - CR', 'attribute_value': None},
                {'label': 'HV - CR', 'is_group': 0, 'attribute': '_Test HV', 'default_value': None, 'from_range': 0.0, 'to_range': 40.0, 'increment': 0.01, 'options': '[]', 'parent_node': 'High Voltage - CR', 'attribute_value': None}
                ]
        })
		self.assertRaises(frappe.ValidationError, ld_duplicate.insert)

        # Worst Case Scenario
		ld_new_doc = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1
        })
		self.assertRaises(frappe.ValidationError, ld_new_doc.insert)
		
	def test_tree_rendering_api_returns_correct_tree_data(self):
        # ---------- Expected Output ----------
		la_expected_output = [
            {
                "value": "High Voltage - CR",
                "expandable": 1,
                "parent_id": "RGB",
                "attribute": "_Test High Voltage",
                "doctype": "Design Configurator",
                
                "from_range": 0.0,
                "to_range": 0.0,
                "increment": 0.0,
                "default_value": None,
                "options": '[{"attribute_value":"_Test HV","abbr":"HV","exclude":0}]'
            },
            {
                "value": "Power - CR",
                "expandable": 1,
                "parent_id": "RGB",
                "attribute": "_Test Power",
                "doctype": "Design Configurator",
               
                "from_range": 0.0,
                "to_range": 0.0,
                "increment": 0.0,
                "default_value": None,
                "options": '[{"attribute_value":"_Test Rating","abbr":"Rating","exclude":0}]'
            }
        ]
        # ---------- Actual Output From API ----------
		la_actual_output = frappe.call(
            "lens_cpq.cpq.doctype.design.api.get_children",
            doctype = "Design",
			parent= "RGB",
			parent_id= "_Test OILTM"
        )
        # print(actual_output)
        # ---------- Compare both ----------
		self.assertCountEqual(
            la_actual_output,
            la_expected_output,
            "Tree Rendering API output does not match expected data!"
        )