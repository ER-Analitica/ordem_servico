from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def pegar_valor_cliente(self, method):
    # Obtém o valor do campo 'tipo_de_faturamento' do cliente associado
    data_limite_de_faturamento_customer = frappe.db.get_value("Customer", self.customer, "data_limite_de_faturamento")
    tipo_faturamento_customer = frappe.db.get_value("Customer", self.customer, "tipo_de_faturamento")
    faturamento_parcial_customer = frappe.db.get_value("Customer", self.customer, "faturamento_parcial")
    confirmacao_do_cliente_customer = frappe.db.get_value("Customer", self.customer, "confirmacao_do_cliente")
    tipo_customer = frappe.db.get_value("Customer", self.customer, "tipo")
    confirmacao_customer = frappe.db.get_value("Customer", self.customer, "confirmacao")
    
    if not self.data_limite_de_faturamento:
        self.data_limite_de_faturamento = data_limite_de_faturamento_customer
    if not self.tipo_de_faturamento:
        self.tipo_de_faturamento = tipo_faturamento_customer
    if not self.faturamento_parcial:
        self.faturamento_parcial = faturamento_parcial_customer
    if not self.confirmacao_do_cliente:
        self.confirmacao_do_cliente = confirmacao_do_cliente_customer
    if not self.tipo:
        self.tipo = tipo_customer
    if not self.confirmacao:
        self.confirmacao = confirmacao_customer
       
        
       
        
  

