from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.sales_order_reference:
        if not self.quotation_name:
            self.quotation_name = frappe.db.get_value("Sales Order", self.sales_order_reference, "quotation_name")

        if self.quotation_name and not self.quotation_date:
            self.quotation_date = frappe.db.get_value("Quotation", self.quotation_name, "transaction_date")

        if not self.sales_order_name:
            self.sales_order_name = self.sales_order_reference

        if not self.sales_order_date:
            self.sales_order_date = frappe.db.get_value("Sales Order", self.sales_order_reference, "transaction_date")
