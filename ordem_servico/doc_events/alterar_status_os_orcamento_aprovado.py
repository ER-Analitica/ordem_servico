from __future__ import unicode_literals
from pydoc import doc
import frappe
from frappe.utils import flt

def on_update_after_submit(self, method):
    previous = self.get_doc_before_save()

    if previous and previous.workflow_state == "Pendente de Aprovação" and self.workflow_state == "Aprovado" and self.os_interna_link and self.os_interna_link.strip() != "":
        os_doc = frappe.get_doc("Ordem Servico Interna", self.os_interna_link)
        os_doc.status_order_service = "Em Conserto"
        os_doc.save(ignore_permissions=True)




