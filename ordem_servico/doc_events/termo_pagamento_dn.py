from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.guia_de_remessa:
        self.payment_terms_template = frappe.db.get_value("Delivery Note", self.guia_de_remessa, "payment_terms_template")
    else:
        self.payment_terms_template = frappe.db.get_value("Sales Order", self.reference_name, "payment_terms_template")
