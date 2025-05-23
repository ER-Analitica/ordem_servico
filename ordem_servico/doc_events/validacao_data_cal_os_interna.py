from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def validate(self, method):
    if self.cal_rbc == 1 or self.cal_rastreavel == 1:
        if not self.data_cal or not self.data_cal_recomendada:
            frappe.throw("Os campos <b>Data da Calibração</b> e/ou <b>Data da Calibração Recomendada</b> são obrigatórios. Verifique e preencha as informações antes de prosseguir.")
