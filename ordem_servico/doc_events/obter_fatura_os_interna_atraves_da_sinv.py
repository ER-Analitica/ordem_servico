from __future__ import unicode_literals
import frappe

from frappe.utils import flt

def obter_fatura_os_interna_atraves_da_sinv (self, method):
        print('ola')
        if self.reference_name:
            sales_invoice_os_interna = frappe.get_all(
            "Ordem Servico Interna", 
            filters={"sales_order_name": self.reference_name},
            fields=["name"] 
        )

            for fatura_os in sales_invoice_os_interna:
                ordem_servico = frappe.get_doc("Ordem Servico Interna", fatura_os['name'])
                ordem_servico.invoice_date = self.posting_date
                ordem_servico.invoice_name = self.name
                ordem_servico.save()
            frappe.db.commit()
             
 

