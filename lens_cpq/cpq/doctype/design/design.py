# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.exceptions import DuplicateEntryError

class Design(Document):


	def autoname(self):
	"""
		Method runs during creation and when `is_template` is enabled,
		it replaces the default system-generated name with `template_name`.

		Raises:
			frappe.ValidationError: If a Design record already exists with the
			same Template Name.
	"""
		if self.is_template and self.template_name:

			# Check for duplicate based on docname
			if frappe.db.exists("Design", self.template_name):
				frappe.throw(
					_("Design Template '{0}' already exists.").format(self.template_name),
					DuplicateEntryError
				)

			# Set the document name as the template name
			self.name = self.template_name

	def validate(self):
	"""
		Method ensures that when a Design is marked as a template (`is_template = 1`),
		a corresponding `template_name` must be provided. 

		Raises:
			frappe.ValidationError: If `is_template` is checked but no Template Name is entered.
	"""
		if self.is_template and not self.template_name:
			frappe.throw(_("Please enter a Template Name."))
