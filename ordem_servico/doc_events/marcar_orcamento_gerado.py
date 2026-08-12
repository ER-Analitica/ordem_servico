"""Marca na OS Interna que o orçamento foi gerado a partir dela.

O `quotation_name` cumpria esse papel: até então ele só era escrito pelo
`set_quotation_history`, no save do orçamento criado pelo botão "Gerar
Orçamento". Depois que o Histórico passou a ser derivado do Pedido de Venda,
o campo também é preenchido em OS que entraram com um pedido pronto — e por
isso deixou de distinguir os dois fluxos.

Este campo tem um dono só: é escrito aqui e em nenhum outro lugar. Serve de
condição para a notificação que avisa o cliente quando o equipamento entra em
conserto após a aprovação do orçamento.

A marcação é feita no servidor, e não no `after_save` do `quotation.js`, para
alcançar também os orçamentos salvos por API ou importação, em que o
JavaScript não roda.
"""

import frappe

DOCTYPE_OS = "Ordem Servico Interna"
CAMPO_OS = "orcamento_gerado_pela_os"


def marcar_na_os(doc, method=None):
    os_nome = (doc.get("os_interna_link") or "").strip()
    if not os_nome:
        return  # orçamento avulso, não nasceu de uma OS

    if not frappe.db.exists(DOCTYPE_OS, os_nome):
        return

    if frappe.db.get_value(DOCTYPE_OS, os_nome, CAMPO_OS):
        return  # já marcado; nada a fazer

    # Gravação direta em vez de doc.save(): rodar o validate completo da OS a
    # partir do salvamento do orçamento poderia falhar por dados não
    # relacionados da OS e impedir que o orçamento fosse salvo.
    frappe.db.set_value(DOCTYPE_OS, os_nome, CAMPO_OS, 1)
    frappe.clear_document_cache(DOCTYPE_OS, os_nome)
