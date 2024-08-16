from __future__ import unicode_literals
import frappe

from datetime import datetime, timedelta

def validate(self, method):
    #try:
        data_atual = frappe.utils.nowdate()
        print(data_atual)
        for documento_interno in self.documentos_internos:
            if documento_interno.data_validade:
                if frappe.utils.get_datetime(documento_interno.data_validade) > frappe.utils.get_datetime(data_atual):
                
                    documento_interno.status = "Em dia"

    #except:
        #frappe.throw("Ocorreu um erro")