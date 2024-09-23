from __future__ import unicode_literals
import frappe

from frappe.utils import flt

def obter_pedido_os_interna(self, method):
    if self.has_quotation_link:
            sales_order_date = frappe.db.get_value(
                "Sales Order", 
                {"quotation_name": self.has_quotation_link}, 
                "transaction_date"
            )
            sales_order_name = frappe.db.get_value(
                "Sales Order", 
                {"quotation_name": self.has_quotation_link}, 
                "name"
            )     
            if sales_order_date:
                # Atribua a data obtida ao campo sales_order_date
                self.sales_order_date = sales_order_date
                self.sales_order_name = sales_order_name
   

