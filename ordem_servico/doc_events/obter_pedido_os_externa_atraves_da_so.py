from __future__ import unicode_literals
import frappe

from frappe.utils import flt

def obter_pedido_os_externa_atraves_da_so (self, method):
        print('ola')
        if self.quotation_name:
            sales_order_quotation_os_externa = frappe.get_all(
            "Ordem Servico Externa", 
            filters={"quotation_name": self.quotation_name},
            fields=["name", "sales_order_date"] 
        )

            for quotation_os in sales_order_quotation_os_externa:
                ordem_servico_externa = frappe.get_doc("Ordem Servico Externa", quotation_os['name'])
                ordem_servico_externa.sales_order_date = self.transaction_date
                ordem_servico_externa.sales_order_name = self.name
                
                ordem_servico_externa.save()
            frappe.db.commit()