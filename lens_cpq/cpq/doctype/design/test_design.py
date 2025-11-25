# Copyright (c) 2025, LMNAs and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


# class TestDesign(FrappeTestCase):
# 	pass
# The responsibility of the api --> return the data in the format that the tree can be displayed
# Test this api
# call the api with args --> parent: RGB, {parent_id: _Test OILT

class TestDesign(FrappeTestCase):

    def test_tree_rendering_api_returns_correct_tree_data(self):
        # ---------- Expected Output ----------
        expected_output = [
            {
                "value": "High Voltage - CR",
                "expandable": 1,
                "parent_id": "RGB",
                "attribute": "High Voltage",
                "doctype": "Design Configurator",
                "name": "2jhpbt1jl3",
                "from_range": 0.0,
                "to_range": 0.0,
                "increment": 0.0,
                "default_value": None,
                "options": '[{"attribute_value":"HV (kV)","abbr":"HV (kV)","exclude":0},{"attribute_value":"HV 2 (kV)","abbr":"HV 2 (kV)","exclude":0},{"attribute_value":"HV Um (kV)","abbr":"HV Um (kV)","exclude":0},{"attribute_value":"HV 1 (kV)","abbr":"HV 1 (kV)","exclude":0}]'
            },
            {
                "value": "Power - CR",
                "expandable": 1,
                "parent_id": "RGB",
                "attribute": "Power",
                "doctype": "Design Configurator",
                "name": "2jh2bavu40",
                "from_range": 0.0,
                "to_range": 0.0,
                "increment": 0.0,
                "default_value": None,
                "options": '[{"attribute_value":"Rating","abbr":"Rating","exclude":0}]'
            }
        ]
        design = frappe.get_doc({
            "doctype": "Design",
            "is_template": 1,
            "template_name": "_Test OILT",
            "design_configurator":[
{'label': 'High Voltage - CR', 'is_group': 1, 'attribute': 'High Voltage', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"HV (kV)","abbr":"HV (kV)","exclude":0},{"attribute_value":"HV 2 (kV)","abbr":"HV 2 (kV)","exclude":0},{"attribute_value":"HV Um (kV)","abbr":"HV Um (kV)","exclude":0},{"attribute_value":"HV 1 (kV)","abbr":"HV 1 (kV)","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
{'label': 'Power - CR', 'is_group': 1, 'attribute': 'Power', 'default_value': None, 'from_range': 0.0, 'to_range': 0.0, 'increment': 0.0, 'options': '[{"attribute_value":"Rating","abbr":"Rating","exclude":0}]', 'parent_node': 'RGB', 'attribute_value': None},
{'label': 'Power (kVA) - CR', 'is_group': 0, 'attribute': 'Power (kVA)', 'default_value': None, 'from_range': 100.0, 'to_range': 25000.0, 'increment': 1.0, 'options': '[]', 'parent_node': 'Power - CR', 'attribute_value': None},
{'label': 'HV (kV) - CR', 'is_group': 0, 'attribute': 'HV (kV)', 'default_value': None, 'from_range': 0.0, 'to_range': 40.0, 'increment': 0.01, 'options': '[]', 'parent_node': 'High Voltage - CR', 'attribute_value': None}
]
                                }).insert()
        # ---------- Actual Output From API ----------
        actual_output = frappe.call(
            method="lens_cpq.doctype.design.api.get_children",
            args={
				"parent": "_Test OILT",
				"kwargs": {"parent_id": "RGB"}
			}
        )

        # ---------- Compare both ----------
        self.assertCountEqual(
            actual_output,
            expected_output,
            "Tree Rendering API output does not match expected data!"
        )
        