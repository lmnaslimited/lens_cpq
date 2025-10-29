# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Design(Document):
	
	def before_save(self):
		# Ensure that the design template is choosen
		if not self.design_template:
			frappe.throw("Design Template is required to generate the name.")

		# Collect all attribute values from the design attributes child table
		la_values = []

		for ld_attr in self.design_attributes:
			la_values.append(ld_attr.attribute_value)

		# Create a suffix string by joining non-empty attribute values with a hyphen
		l_suffix = "-".join([str(l_value) for l_value in la_values if l_value is not None and l_value != ""])

		# Construct the final design name as <design_template>-<attribute_values>
		self.name = f"{self.design_template}-{l_suffix}"