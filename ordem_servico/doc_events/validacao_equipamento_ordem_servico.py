from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validacao_equipamento_ordem_servico(self, method):
    if self.serie_number:
        equipamento_cliente = frappe.db.get_value("Equipamentos", self.serie_number, "customer")

        if self.customer != equipamento_cliente:
            frappe.throw(("O equipamento com o número de série {0} não pertence ao cliente {1}.").format(self.serie_number, self.customer))
