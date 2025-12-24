# Copyright (c) 2025, LMNAs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils.caching import redis_cache


class ConditionType(Document):
	pass


'''
@redis_cache()
Decorator to cache method calls and its return values in Redis

args:

ttl: time to expiry in seconds, defaults to 1 hour
user: true should cache be specific to session user.
shared: true should cache be shared across sites
'''
@frappe.whitelist()
@redis_cache()
def get_condition_type_doctypes():
	doctypes = []
	data = frappe.get_all("Condition Type", {"enable": 1}, ["document_reference"], distinct=1)

	for entry in data:
		doctypes.append(entry.document_reference)

	return doctypes


def add_ct_doctypes(bootinfo):
	bootinfo.condition_type_doctypes = get_condition_type_doctypes()