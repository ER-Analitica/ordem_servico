from __future__ import unicode_literals
import frappe

from frappe.utils import flt

def obter_fatura_os_externa_atraves_da_sinv (self, method):
        print('ola')
        if self.reference_name:
            sales_invoice_os_externa = frappe.get_all(
            "Ordem Servico Externa", 
            filters={"sales_order_name": self.reference_name},
            fields=["name"] 
        )

            for fatura_os in sales_invoice_os_externa:
                ordem_servico = frappe.get_doc("Ordem Servico Externa", fatura_os['name'])
                ordem_servico.invoice_date = self.posting_date
                ordem_servico.invoice_name = self.name
                ordem_servico.save()
            frappe.db.commit()
             
 

