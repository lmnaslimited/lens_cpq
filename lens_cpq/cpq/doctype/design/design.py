# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.exceptions import DuplicateEntryError

class Design(Document):
	
	"""
		Method runs during creation and when `is_template` is enabled,
		it replaces the default system-generated name with `template_name`.

		Raises:
			frappe.ValidationError: If a Design record already exists with the
			same Template Name.
	"""
	def autoname(self):
		if self.is_template and self.template_name:

			try:
				# Check for duplicate based on docname
				if frappe.db.exists("Design", self.template_name):
					frappe.throw(
						f"Design Template '{self.template_name}' already exists.",
						DuplicateEntryError
					)

			except DuplicateEntryError:
				frappe.msgprint("A duplicate entry was found. Skipping.")
				return

			# Set the document name
			self.name = self.template_name

	def validate(self):
		# Ensure that template_name is set if is_template is True
		if self.is_template and not self.template_name:
			frappe.throw("Enter Template Name")