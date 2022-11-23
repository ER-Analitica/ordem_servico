from __future__ import unicode_literals
import frappe

def execute():
    frappe.db.sql("""
        UPDATE `tabCustomer` SET `cnpj` = `tax_id`
    """)