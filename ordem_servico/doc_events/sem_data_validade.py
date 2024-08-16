from __future__ import unicode_literals
import frappe

def validate(self, method):
    try:
        for documento_interno in self.documentos_internos:
            if documento_interno.validade == 0:
                documento_interno.data_validade = ""

    except:
        frappe.throw("Ocorreu um erro")