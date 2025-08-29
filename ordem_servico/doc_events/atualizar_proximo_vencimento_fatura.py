from __future__ import unicode_literals
import frappe
from frappe.utils import formatdate

def atualizar_proximo_vencimento_fatura(doc, method):
    for ref in doc.references:
        if ref.reference_doctype == "Sales Invoice":
            invoice = frappe.get_doc("Sales Invoice", ref.reference_name)
            
            # pega apenas os pagamentos ainda em aberto
            parcelas_abertas = [p for p in invoice.payment_schedule if p.outstanding > 0]

            if parcelas_abertas:
                # pega a primeira parcela com menor due_date
                proxima = min(parcelas_abertas, key=lambda x: x.due_date)

                # Formata data
                data_formatada = formatdate(proxima.due_date, "dd/mm/yyyy")

                # Formata valor para R$
                valor_formatado = f"R$ {proxima.payment_amount:,.2f}".replace(".", ",").replace(",", ".", 1)

                invoice.custom_proximo_vencimento = data_formatada
                invoice.custom_proxima_parcela = valor_formatado
            else:
                invoice.custom_proximo_vencimento = "Fatura quitada"
                invoice.custom_proxima_parcela = "Nenhuma parcela pendente"

            invoice.save(ignore_permissions=True)
