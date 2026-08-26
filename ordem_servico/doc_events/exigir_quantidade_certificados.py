"""Quantidade de Certificados obrigatória depois que o conserto começa.

O campo fica no Laudo Final e é preenchido pelo técnico. Como nada o cobrava,
OS chegavam ao fim sem essa informação.

**Por que a cobrança só vale do segundo save em diante:** o botão "Iniciar
Manutenção" preenche o `start_repair_time` e salva a OS no mesmo movimento
(`utils.get_time_now`). Cobrar já nesse save impediria o técnico de iniciar o
conserto — ele precisaria preencher a quantidade antes de começar o trabalho
que gera os certificados. Por isso o corte é o save anterior: se o conserto já
tinha começado, a quantidade passa a ser exigida.

Na prática o técnico inicia o conserto normalmente e, na primeira vez que for
salvar a OS depois disso — inclusive ao finalizar a manutenção, que também
salva —, o campo é cobrado.

Vale para as duas OS: os dois doctypes têm o `start_repair_time` e o campo.
"""

import frappe

CAMPO = "custom_quantidade_certificados"
CAMPO_INICIO = "start_repair_time"


def _preenchido(valor):
    return bool((valor or "").strip()) if isinstance(valor, str) else bool(valor)


def exigir_quantidade(doc, method=None):
    """Gatilho no validate das duas OS."""
    anterior = doc.get_doc_before_save()
    if not anterior:
        return  # OS sendo criada agora

    # O conserto está começando exatamente neste save: deixa passar, senão o
    # botão "Iniciar Manutenção" nunca conseguiria concluir.
    if not _preenchido(anterior.get(CAMPO_INICIO)):
        return

    if not _preenchido(doc.get(CAMPO_INICIO)):
        return  # conserto ainda não iniciado

    if _preenchido(doc.get(CAMPO)):
        return

    frappe.throw(
        "Preencha a <b>Quantidade Certificados</b> antes de salvar.<br><br>"
        "O conserto já foi iniciado, e é essa informação que registra quantos "
        "certificados a OS vai gerar.",
        title="Quantidade Certificados em falta",
    )
