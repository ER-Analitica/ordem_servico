from __future__ import unicode_literals
import frappe
from frappe.utils import flt, formatdate

def atualizar_vencimento_fatura(doc, method):
    """
    Atualiza os campos Próximo Vencimento e Próxima Parcela
    com o primeiro vencimento da Payment Schedule.
    """
    if not doc.payment_schedule:
        doc.db_set("custom_proximo_vencimento", "Fatura quitada")
        doc.db_set("custom_proximo_vencimento_email_automatico", None)
        doc.db_set("custom_proxima_parcela", "Nenhuma parcela pendente")
        return

    # percorre a payment_schedule e pega a primeira parcela
    primeira_parcela = doc.payment_schedule[0]
    due_date = primeira_parcela.due_date
    # Formatar data no padrão brasileiro
    data_formatada = formatdate(primeira_parcela.due_date, "dd/mm/yyyy")

    # Formatar valor em R$
    valor_formatado = f"R$ {primeira_parcela.payment_amount:,.2f}" \
        .replace(".", ",") \
        .replace(",", ".", 1)

    doc.db_set("custom_proximo_vencimento", data_formatada)
    doc.db_set("custom_proximo_vencimento_email_automatico", due_date)
    doc.db_set("custom_proxima_parcela", valor_formatado)
