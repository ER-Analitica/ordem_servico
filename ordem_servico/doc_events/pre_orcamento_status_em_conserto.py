from __future__ import unicode_literals
from pydoc import doc
import frappe
from frappe.utils import flt

def before_save(self, method):
    if (
        self.have_quotation == 1
        and self.has_quotation_link
        and self.has_quotation_link.strip() != ""
        and self.status_order_service == "Em Recebimento"
    ):
        self.status_order_service = "Em Conserto"





