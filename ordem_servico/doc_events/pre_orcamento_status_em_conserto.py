from __future__ import unicode_literals
from pydoc import doc
import frappe
from frappe.utils import flt

def before_save(self, method):
    """OS que já entra com pré-orçamento fechado vai direto para conserto.

    Vale para os dois vínculos: o Pedido de Venda (fluxo atual) e o Orçamento
    (fluxo antigo, mantido para as OS já existentes).
    """
    if self.status_order_service != "Em Recebimento":
        return

    tem_pedido = (
        self.get("possui_pedido_venda") == 1
        and (self.get("has_sales_order_link") or "").strip() != ""
    )
    tem_orcamento = (
        self.get("have_quotation") == 1
        and (self.get("has_quotation_link") or "").strip() != ""
    )

    if tem_pedido or tem_orcamento:
        self.status_order_service = "Em Conserto"





