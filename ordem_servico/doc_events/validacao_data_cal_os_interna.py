from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.cal_rbc == 1 or self.cal_rastreavel == 1:
        if not self.data_cal:
            frappe.throw("Você precisa informar a <b>Data da Calibração</b> para continuar. Verifique e preencha este campo antes de prosseguir.")
