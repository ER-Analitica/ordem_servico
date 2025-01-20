from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validacao_uf_quotation (self, method):
    if self.uf == "":
        frappe.throw("O campo 'UF' está vazio. Por favor, altere o campo 'Endereço Para Entrega' e insira-o novamente para que a informação da UF seja preenchida corretamente antes de prosseguir.")
