from __future__ import unicode_literals
import frappe
from frappe.utils import flt


def validate(self, method):
    if self.fatura_de_venda:
        self.payment_terms_template = frappe.db.get_value("Sales Invoice", self.fatura_de_venda, "payment_terms_template")
