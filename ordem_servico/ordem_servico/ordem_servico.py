# -*- coding: utf-8 -*-
# Copyright (c) 2017, laugusto and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

@frappe.whitelist()
def rename_os(doc_maint):
	maint = frappe.get_doc("Maintenance Visit", doc_maint)
	len_array_purposes = len(maint.purposes)
	idx = 0
	for idx in range(len_array_purposes):
		maint.purposes[idx].os = "OS-%s/%s" % (maint.name, str(idx))
	maint.save()
	return

@frappe.whitelist()
def make_orcamento(doc_maint, purposes_os):
	maint = frappe.get_doc("Maintenance Visit", doc_maint)
	quotation = frappe.new_doc("Quotation")
	quotation.os_doctype = "Maintenance Visit"
	quotation.os_link = maint.name
	quotation.naming_series = "%s .#" % purposes_os
	quotation.customer = maint.customer_name
	quotation.flags.ignore_mandatory = True
	quotation.flags.ignore_validate = True
	quotation.save()
	return quotation