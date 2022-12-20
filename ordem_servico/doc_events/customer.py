from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.cnpj:
        self.tax_id = self.cnpj
