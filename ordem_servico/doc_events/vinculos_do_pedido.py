"""Traz para o Histórico da OS os documentos que o pedido já tem.

O Histórico da OS se enchia aos poucos, e só para a frente: cada documento se
gravava na OS no momento em que era criado. Isso deixava um buraco — quando o
técnico vincula um pedido que **já** tem nota de entrega, fatura ou pagamento,
esses documentos nasceram antes do vínculo existir e nunca se registravam.
A OS ficava mostrando pedido sem fatura, e o relatório não fechava.

Aqui o caminho é o inverso: partindo do pedido vigente do Histórico, procuramos
o que já existe e trazemos. A Nota Fiscal e a Nota de Entrega apontam para o
pedido pelo `reference_name`; o Pagamento chega pela fatura, na tabela de
referências que o próprio ERPNext mantém.

Duas situações, regras diferentes:

* **Campo vazio** — preenchemos com o que o pedido tiver. É o buraco original.
* **Pedido trocado** — os vínculos acompanham o pedido novo, senão a OS ficaria
  mostrando a fatura de um pedido e o número de outro.

O que **não** fazemos é apagar documento que nunca foi do pedido. A maior parte
das faturas e notas de entrega aqui chega na OS direto pelo `os_interna_link`,
sem `reference_name` nenhum — espelhar o pedido cegamente apagaria milhares
delas. Por isso, na troca, só sai o vínculo que comprovadamente pertencia ao
pedido anterior.

Documento cancelado é ignorado: só entra o que está enviado.

A OS Externa não tem Nota de Entrega nem Pagamento no Histórico; lá o módulo
traz apenas a Nota Fiscal, que é o que existe.
"""

import re

import frappe

CAMPO_PEDIDO = "sales_order_name"

# (campo do nome, campo da data) por doctype de origem. A OS que não tiver o
# campo é simplesmente pulada — é assim que a Externa fica só com a fatura.
DESTINOS = {
    "Sales Invoice": ("invoice_name", "invoice_date"),
    "Delivery Note": ("delivery_note_name", "delivery_note_date"),
    "Payment Entry": ("payment_entry_name", "payment_entry_date"),
}


def _mais_recente(doctype, filtros):
    """Documento enviado mais recente que casa com os filtros."""
    filtros = dict(filtros)
    filtros["docstatus"] = 1
    achados = frappe.get_all(
        doctype,
        filters=filtros,
        fields=["name", "posting_date"],
        order_by="posting_date desc, creation desc",
        limit=1,
    )
    return achados[0] if achados else None


def _pagamento_da_fatura(fatura):
    """Pagamento que quita a fatura, pela tabela de referências do ERPNext."""
    if not fatura:
        return None

    nomes = frappe.get_all(
        "Payment Entry Reference",
        filters={"reference_doctype": "Sales Invoice", "reference_name": fatura, "docstatus": 1},
        pluck="parent",
    )
    if not nomes:
        return None

    return _mais_recente("Payment Entry", {"name": ("in", nomes)})


def _dono_do_documento(doctype, nome):
    """Pedido ao qual o documento pertence, ou None se ele for direto da OS."""
    if not nome:
        return None
    return frappe.db.get_value(doctype, nome, "reference_name") or None


def preencher_vinculos(doc, method=None):
    """Gatilho no validate das OS, depois que o Histórico já resolveu o pedido."""
    anterior = doc.get_doc_before_save()
    pedido_antes = (anterior.get(CAMPO_PEDIDO) or "").strip() if anterior else ""
    pedido = (doc.get(CAMPO_PEDIDO) or "").strip()

    trocou = bool(anterior) and pedido != pedido_antes

    if not pedido and not trocou:
        return

    fatura = _mais_recente("Sales Invoice", {"reference_name": pedido}) if pedido else None
    guia = _mais_recente("Delivery Note", {"reference_name": pedido}) if pedido else None

    achados = {"Sales Invoice": fatura, "Delivery Note": guia}

    for doctype in ("Sales Invoice", "Delivery Note"):
        campo, campo_data = DESTINOS[doctype]
        if not doc.meta.has_field(campo):
            continue  # a OS Externa não tem nota de entrega

        encontrado = achados[doctype]
        atual = doc.get(campo)

        if encontrado:
            # O pedido tem o documento: entra quando o campo está vazio, e
            # substitui quando o pedido mudou.
            if not atual or trocou:
                doc.set(campo, encontrado.name)
                doc.set(campo_data, encontrado.posting_date)
        elif trocou and atual and _dono_do_documento(doctype, atual) == pedido_antes:
            # Era do pedido anterior e o pedido novo não tem equivalente. Sai,
            # senão a OS ficaria com documento de um pedido que não é mais o
            # dela. Documento sem dono (direto da OS) permanece.
            doc.set(campo, None)
            doc.set(campo_data, None)

    _ajustar_pagamento(doc, trocou)


def _ajustar_pagamento(doc, trocou):
    """O pagamento segue a fatura: não existe vínculo dele com o pedido."""
    campo, campo_data = DESTINOS["Payment Entry"]
    if not doc.meta.has_field(campo):
        return  # a OS Externa não tem pagamento

    fatura = doc.get(DESTINOS["Sales Invoice"][0])

    if not fatura:
        # Sem fatura não há pagamento a mostrar. Só limpamos numa troca de
        # pedido, para não apagar o que outra rotina tenha registrado.
        if trocou and doc.get(campo):
            doc.set(campo, None)
            doc.set(campo_data, None)
        return

    if doc.get(campo) and not trocou:
        return  # já tem, e o pedido não mudou

    pagamento = _pagamento_da_fatura(fatura)
    if pagamento:
        doc.set(campo, pagamento.name)
        doc.set(campo_data, pagamento.posting_date)
    elif trocou:
        doc.set(campo, None)
        doc.set(campo_data, None)


# --------------------------------------------------------------------------
# Aviso de documento cancelado ainda sem substituto
# --------------------------------------------------------------------------
#
# A substituição já funciona sozinha: o documento refeito se grava na OS ao ser
# enviado. O buraco é a janela entre o cancelamento e o substituto — e o caso em
# que substituto nenhum aparece. Aí o Histórico segue apontando para um
# documento que não vale mais, sem dizer nada.
#
# É o mesmo tratamento que o `historico_pedido` já dá ao Pedido e ao Orçamento
# cancelados sem retificação, estendido aos três documentos que ficaram de fora.

CAMPO_OBS = "obs_historico"

# (campo, rótulo, adjetivo) — o adjetivo acompanha o gênero do documento.
AVISAVEIS = (
    ("invoice_name", "Nota Fiscal", "cancelada"),
    ("delivery_note_name", "Nota de Entrega", "cancelada"),
    ("payment_entry_name", "Pagamento", "cancelado"),
)

DOCTYPE_DO_CAMPO = {
    "invoice_name": "Sales Invoice",
    "delivery_note_name": "Delivery Note",
    "payment_entry_name": "Payment Entry",
}

# Reconhece os avisos que este módulo escreveu, para refazê-los a cada save em
# vez de empilhar. Sem isso a observação cresceria sem parar.
PADRAO_AVISO = re.compile(
    r"^(?:Nota Fiscal|Nota de Entrega|Pagamento) .+ cancelad[ao], sem substituição\.$",
    re.MULTILINE,
)


def _avisos_para(valores, tem_campo):
    """Avisos que a OS deve exibir, a partir dos vínculos que ela tem hoje."""
    avisos = []
    for campo, rotulo, adjetivo in AVISAVEIS:
        if not tem_campo(campo):
            continue  # a OS Externa só tem a Nota Fiscal
        nome = (valores.get(campo) or "").strip()
        if not nome:
            continue
        if frappe.db.get_value(DOCTYPE_DO_CAMPO[campo], nome, "docstatus") == 2:
            avisos.append("{} {} {}, sem substituição.".format(rotulo, nome, adjetivo))
    return avisos


def _observacao_atualizada(obs_atual, avisos):
    """Troca os avisos da rodada anterior pelos desta, preservando o resto."""
    limpo = "\n".join(
        linha
        for linha in (obs_atual or "").split("\n")
        if not PADRAO_AVISO.match(linha.strip())
    ).strip()
    return "\n".join([p for p in (limpo, "\n".join(avisos)) if p]).strip() or None


def sinalizar_cancelados(doc, method=None):
    """Gatilho no validate das duas OS — mantém os avisos em dia a cada save."""
    avisos = _avisos_para(doc, doc.meta.has_field)
    doc.set(CAMPO_OBS, _observacao_atualizada(doc.get(CAMPO_OBS), avisos))


def _recalcular_na_os(doctype_os, os_name):
    """Reescreve os avisos direto na tabela, sem passar pelo validate da OS.

    O `save()` roda as validações inteiras, e as OS antigas não passam nelas —
    um cancelamento de fatura não pode falhar por causa de um campo obrigatório
    criado anos depois, sem relação nenhuma com o que está acontecendo.
    """
    meta = frappe.get_meta(doctype_os)
    campos = [c for c, _r, _a in AVISAVEIS if meta.has_field(c)]

    valores = frappe.db.get_value(doctype_os, os_name, campos + [CAMPO_OBS], as_dict=True)
    if not valores:
        return

    avisos = _avisos_para(valores, meta.has_field)
    nova = _observacao_atualizada(valores.get(CAMPO_OBS), avisos)

    if nova == (valores.get(CAMPO_OBS) or None):
        return  # nada mudou

    frappe.db.set_value(doctype_os, os_name, CAMPO_OBS, nova, update_modified=False)
    frappe.clear_document_cache(doctype_os, os_name)


def marcar_cancelamento_na_os(doc, method=None):
    """Gatilho no cancelamento da Nota Fiscal, da Nota de Entrega e do Pagamento.

    Sem isto o aviso só nasceria no próximo save da OS — que pode não acontecer
    nunca. Aqui ele aparece no instante do cancelamento.
    """
    campo = next((c for c, dt in DOCTYPE_DO_CAMPO.items() if dt == doc.doctype), None)
    if not campo:
        return

    for doctype_os in ("Ordem Servico Interna", "Ordem Servico Externa"):
        if not frappe.get_meta(doctype_os).has_field(campo):
            continue
        for os_name in frappe.get_all(doctype_os, filters={campo: doc.name}, pluck="name"):
            _recalcular_na_os(doctype_os, os_name)


# --------------------------------------------------------------------------
# Retificação: o documento novo assume o lugar do que ele corrigiu
# --------------------------------------------------------------------------
#
# O Pedido e o Orçamento já seguem a retificação, por `historico_pedido`. A Nota
# Fiscal, a Nota de Entrega e o Pagamento não seguiam — e por um motivo que não
# dá para corrigir na origem: o `set_delivery_note_history` e o
# `set_payment_entry_history` só gravam quando o campo está **vazio**, então o
# documento refeito era ignorado enquanto o cancelado ocupasse o lugar. (Na
# Nota Fiscal essa trava está comentada, e é por isso que só ela funcionava.)
#
# A ligação usada aqui é o `amended_from`, que o próprio Frappe grava ao
# retificar. Ela não depende do `reference_name` — o que importa, porque quase
# nenhuma Nota de Entrega aqui aponta para o pedido.


def assumir_lugar_do_retificado(doc, method=None):
    """Gatilho no envio da Nota Fiscal, da Nota de Entrega e do Pagamento."""
    corrigido = (doc.get("amended_from") or "").strip()
    if not corrigido:
        return  # documento novo, não é retificação de ninguém

    doctype_origem = doc.doctype
    par = DESTINOS.get(doctype_origem)
    if not par:
        return
    campo, campo_data = par

    for doctype_os in ("Ordem Servico Interna", "Ordem Servico Externa"):
        meta = frappe.get_meta(doctype_os)
        if not meta.has_field(campo):
            continue  # a OS Externa não tem nota de entrega nem pagamento

        alcancadas = frappe.get_all(doctype_os, filters={campo: corrigido}, pluck="name")
        for os_name in alcancadas:
            frappe.db.set_value(
                doctype_os,
                os_name,
                {campo: doc.name, campo_data: doc.get("posting_date")},
                update_modified=False,
            )
            frappe.clear_document_cache(doctype_os, os_name)
            # O aviso de cancelamento perde o motivo de existir agora.
            _recalcular_na_os(doctype_os, os_name)
