from __future__ import unicode_literals

import frappe


def obter_pedido_os_interna(self, method=None):
    """Preenche o Histórico da OS Interna com pedido e orçamento.

    Fluxo atual: a OS aponta para o Pedido de Venda (has_sales_order_link).
    A partir dele buscamos o orçamento que o originou e as duas datas.

    Fluxo antigo: as OS criadas antes usavam o Orçamento (has_quotation_link)
    e o pedido era descoberto a partir dele. Esse caminho continua funcionando
    para não alterar o histórico já registrado.
    """
    pedido = (self.get("has_sales_order_link") or "").strip()

    if pedido:
        dados = frappe.db.get_value(
            "Sales Order", pedido, ["transaction_date", "quotation_name"], as_dict=True
        )
        if dados:
            self.sales_order_name = pedido
            self.sales_order_date = dados.transaction_date

            # Orçamento que originou o pedido (o aprovado)
            if dados.quotation_name:
                self.quotation_name = dados.quotation_name
                self.quotation_date = frappe.db.get_value(
                    "Quotation", dados.quotation_name, "transaction_date"
                )
        return

    # Pedido removido nesta edição: limpa o histórico que ele havia preenchido.
    # Sem isso o `quotation_name` ficaria preso e o botão "Gerar Orçamento"
    # nunca mais voltaria a aparecer.
    anterior = self.get_doc_before_save()
    if anterior and (anterior.get("has_sales_order_link") or "").strip():
        self.sales_order_name = None
        self.sales_order_date = None
        self.quotation_name = None
        self.quotation_date = None

    # --- compatibilidade com as OS antigas, vinculadas ao orçamento ---
    if self.get("has_quotation_link"):
        sales_order = frappe.db.get_value(
            "Sales Order",
            {"quotation_name": self.has_quotation_link},
            ["name", "transaction_date"],
            as_dict=True,
        )
        if sales_order:
            self.sales_order_name = sales_order.name
            self.sales_order_date = sales_order.transaction_date
