# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class Design(Document):

	"""
		Method runs during creation and when `is_template` is enabled,
		it replaces the default system-generated name with `template_name`.

        Raises: frappe.ValidationError: If a Design record already exists with the 
        same Template Name.
    """

	def autoname(self):
		if self.is_template and self.template_name:
			# Check for duplicate design document name
			if frappe.db.exists("Design", self.template_name):
				frappe.throw(f"Design Template '{self.template_name}' already exists.")

			# Set the document name
			self.name = self.template_name