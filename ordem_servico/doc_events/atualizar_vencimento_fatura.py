from __future__ import unicode_literals
import frappe
from frappe.utils import flt

def atualizar_vencimento_fatura(doc, method):
    """
    Atualiza os campos Próximo Vencimento e Próxima Parcela
    com o primeiro vencimento da Payment Schedule.
    """
    if not doc.payment_schedule:
        doc.db_set("custom_proximo_vencimento", "Fatura quitada")
        doc.db_set("custom_proxima_parcela", "Nenhuma parcela pendente")
        return

    # percorre a payment_schedule e pega a primeira parcela
    primeira_parcela = doc.payment_schedule[0]

    doc.db_set("custom_proximo_vencimento", primeira_parcela.due_date)
    doc.db_set("custom_proxima_parcela", primeira_parcela.payment_amount)