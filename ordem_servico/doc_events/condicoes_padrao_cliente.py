"""Condições e Prazo de Pagamento do cliente no orçamento gerado pela OS.

O caso do **orçamento avulso** não passa por aqui: os campos têm "Buscar De"
apontando para o cliente, e o próprio Frappe preenche assim que a pessoa
escolhe o cliente na tela. Como está configurado com `fetch_if_empty`, o que
for digitado ali é respeitado — inclusive antes do primeiro save.

Este módulo cobre só o **orçamento gerado pela OS**, onde o "Buscar De" não
tem chance de agir: o `make_quotation` grava `tc_name = "Boleto 15 dias"` fixo
para todo mundo, e o Frappe só busca do cliente quando o campo está vazio.

Por isso aqui a regra é sobrescrever, e não completar: no primeiro save o que
está cadastrado no cliente passa por cima do valor fixo — inclusive quando o
cliente está sem padrão, caso em que o campo fica em branco para ser
preenchido à mão. Do segundo save em diante ninguém mexe, e a exceção
combinada para aquela compra permanece.
"""

import frappe

CAMPOS = ("tc_name", "prazo_de_pagamento")


def herdar_do_cliente(doc, method=None):
    # Só no primeiro save: depois disso o orçamento é dono do que tem.
    if not doc.is_new():
        return

    # Só no que veio da OS. No avulso quem preenche é o "Buscar De", que
    # respeita a escolha de quem está montando o orçamento.
    if not (doc.get("os_interna_link") or "").strip():
        return

    # O orçamento também pode ser emitido para um Lead, que não tem esses
    # campos. O `party_name` é um Dynamic Link: só vale como cliente quando o
    # `quotation_to` diz que é.
    if doc.get("quotation_to") != "Customer":
        return

    cliente = (doc.get("party_name") or "").strip()
    if not cliente:
        return

    padrao = frappe.db.get_value("Customer", cliente, list(CAMPOS), as_dict=True)
    if not padrao:
        return

    for campo in CAMPOS:
        doc.set(campo, padrao.get(campo) or None)
