# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Design(Document):
	def before_save(self):
		if not self.design_template:
			frappe.throw("Design Template is required to generate the name.")

		la_values = []

		for ld_attr in self.design_attributes:
			la_values.append(ld_attr.attribute_value)

		l_suffix = "-".join([str(value) for value in la_values if value is not None and value != ""])

		self.name = f"{self.design_template}-{l_suffix}"