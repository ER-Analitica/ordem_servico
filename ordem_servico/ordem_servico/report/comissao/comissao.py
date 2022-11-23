# Copyright (c) 2013, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe

def execute(filters=None):
	if not filters: filters = {}

	columns = get_columns()
	data = get_comission(filters)

	return columns, data


def get_columns():
	return [
		("OS"),
		("Equipamento"),
		("Nome"),
		("Status")
	]

def get_comission(filters):
	return frappe.db.sql("SELECT name, equipment_description, repaired_by_name, status_order_service FROM `tabOrdem Servico Interna` WHERE status_order_service = 'Encerrada' UNION ALL SELECT name, equipment_description, repaired_by_name, status_order_service FROM `tabOrdem Servico Externa` WHERE status_order_service = 'Encerrada'")