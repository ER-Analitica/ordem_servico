from __future__ import unicode_literals
import frappe

from frappe.utils import flt

def obter_pedido_os_interna_atraves_da_so (self, method):
        print('ola')
        if self.quotation_name:
            sales_order_quotation_os_interna = frappe.get_all(
            "Ordem Servico Interna", 
            filters={"has_quotation_link": self.quotation_name},
            fields=["name", "sales_order_date"] 
        )

            for quotation_os in sales_order_quotation_os_interna:
                ordem_servico = frappe.get_doc("Ordem Servico Interna", quotation_os['name'])
                ordem_servico.sales_order_date = self.transaction_date
                ordem_servico.sales_order_name = self.name
                ordem_servico.save()
            frappe.db.commit()
             
 

