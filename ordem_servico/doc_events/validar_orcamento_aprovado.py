"""Só deixa enviar o Pedido de Venda com o orçamento vinculado aprovado.

Havia um Client Script fazendo essa checagem, mas ele consultava o orçamento
com `frappe.call` assíncrono dentro do `validate`: o handler terminava antes da
resposta chegar, então o `frappe.validated = false` era tarde demais — a
mensagem de erro aparecia e o documento salvava assim mesmo. Seis pedidos já
foram enviados com o orçamento em "Pendente de Aprovação" por causa disso.

Aqui a checagem é no servidor e no `before_submit`: o pedido continua podendo
ser salvo em rascunho enquanto o orçamento não sai, e só o envio é barrado.
"""

import frappe

ESTADO_APROVADO = "Aprovado"


def exigir_orcamento_aprovado(self, method=None):
    orcamento = (self.get("quotation_name") or "").strip()
    if not orcamento:
        return  # pedido avulso, sem orçamento de origem

    estado = frappe.db.get_value("Quotation", orcamento, "workflow_state")
    if estado == ESTADO_APROVADO:
        return

    frappe.throw(
        "Este pedido só pode ser enviado com o orçamento aprovado.<br><br>"
        "O orçamento <b>{}</b> está em <b>{}</b>.".format(
            orcamento, estado or "situação não definida"
        ),
        title="Orçamento não aprovado",
    )
