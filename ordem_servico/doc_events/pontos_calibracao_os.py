"""Pontos de Calibração e Critérios de Aceitação: do Pedido de Venda para a OS.

A origem é sempre o **Pedido de Venda**. O Orçamento chegou a ser usado como
reserva, mas isso trazia texto de um documento que não é o que foi vendido — e
depois de uma retificação do pedido esse texto ficava preso na OS. Para o
vínculo valer, `exigir_pontos_no_pedido` não deixa enviar pedido sem pontos.

Na OS o campo continua editável e o que for escrito ali é preservado: o técnico
ajusta os pontos para o caso concreto. Por isso, no save, só preenchemos quando
o campo está vazio. Trocar o pedido no formulário substitui (ver
`itens_pedido_venda.js`), e a retificação atualiza o que ainda não foi editado
(ver `historico_pedido`).
"""

import re

import frappe

CAMPO_OS = "pontos_cal_criterios_aceitacao"
CAMPO_ORIGEM = "pontos_de_calibracao"

TAGS = re.compile(r"<[^>]+>")


def normalizar(texto):
    """Só o texto, sem a marcação do editor.

    Serve para comparar conteúdo: o mesmo texto pode chegar como
    `<p>x</p>` de um lado e `<div class="ql-editor"><p>x</p></div>` do outro.
    """
    if not texto:
        return ""
    return " ".join(TAGS.sub(" ", texto).replace("&nbsp;", " ").split())


def vazio(texto):
    """Um Text Editor "vazio" costuma trazer sobras de HTML, não string vazia."""
    return not normalizar(texto)


def exigir_pontos_no_pedido(self, method=None):
    """Gatilho no before_submit do Pedido — os pontos são obrigatórios.

    Barramos aqui, e não no save da OS, porque depois do envio o campo do
    pedido fica bloqueado: uma OS presa por falta de pontos não teria como ser
    destravada sem cancelar e retificar o pedido inteiro.
    """
    if vazio(self.get(CAMPO_ORIGEM)):
        frappe.throw(
            "Preencha os <b>Pontos de Calibração</b> antes de enviar o pedido.<br><br>"
            "É deles que as Ordens de Serviço tiram os Critérios de Aceitação.",
            title="Pontos de Calibração em falta",
        )


def escolher_pontos(pedido):
    """Pontos do pedido, ou None se ele não tiver."""
    pedido = (pedido or "").strip()
    if not pedido:
        return None

    pontos = frappe.db.get_value("Sales Order", pedido, CAMPO_ORIGEM)
    return None if vazio(pontos) else pontos


def preencher_pontos(doc, method=None):
    """Gatilho no validate das OS — preenche o campo quando está vazio."""
    if not vazio(doc.get(CAMPO_OS)):
        return  # já tem conteúdo, possivelmente ajustado à mão

    novo = escolher_pontos(doc.get("sales_order_name"))
    if novo:
        doc.set(CAMPO_OS, novo)
