from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.sales_order_reference:
        if not self.data_do_servico:
            self.data_do_servico = frappe.db.get_value("Sales Order", self.sales_order_reference, "data_do_servico")
        if not self.integracao:
            self.integracao = frappe.db.get_value("Sales Order", self.sales_order_reference, "integracao")
        if not self.data_integracao:
            self.data_integracao = frappe.db.get_value("Sales Order", self.sales_order_reference, "data_integracao")
        if not self.hora_integracao:
            self.hora_integracao = frappe.db.get_value("Sales Order", self.sales_order_reference, "hora_integracao")
        if not self.endereco_empresa:
            self.endereco_empresa = frappe.db.get_value("Sales Order", self.sales_order_reference, "shipping_address_name")
        if not self.observacoes_visita:
            self.observacoes_visita = frappe.db.get_value("Sales Order", self.sales_order_reference, "observacoes_visita")
        if not self.pontos_calibracao:
            self.pontos_calibracao = frappe.db.get_value("Sales Order", self.sales_order_reference, "pontos_de_calibracao")

