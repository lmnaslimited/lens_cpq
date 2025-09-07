# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

##
import frappe
from frappe.utils.caching import redis_cache
##
from frappe.model.document import Document


class ConditionType(Document):
	pass

@frappe.whitelist()
# @redis_cache()
def get_condition_doctypes():
	doctypes = []
	data = frappe.get_all("Condition Type", {"enable": 1}, ["document_reference"], distinct=1)

	for entry in data:
		doctypes.append(entry.document_reference)

	return doctypes


def add_condition_doctypes(bootinfo):
	bootinfo.condition_type_doctypes = get_condition_doctypes()