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

**Por que só vale no save feito na própria OS:** vários documentos gravam o
Histórico salvando a OS por baixo — o orçamento, o pedido, a nota de entrega, a
fatura e o pagamento todos chamam `os_doc.save()`. Sem este recorte, uma OS
antiga sem a quantidade preenchida derrubaria o save daqueles documentos, e
quem estivesse emitindo uma fatura receberia o erro de uma OS que não está nem
olhando.

A cobrança existe para o técnico que trabalha na OS. Fora dali ela só atrapalha.

Vale para as duas OS: os dois doctypes têm o `start_repair_time` e o campo.
"""

import frappe

CAMPO = "custom_quantidade_certificados"
CAMPO_INICIO = "start_repair_time"


def _preenchido(valor):
    return bool((valor or "").strip()) if isinstance(valor, str) else bool(valor)


def _salvando_a_propria_os(doc):
    """A OS é o documento que a pessoa está salvando, e não efeito colateral.

    O save feito pela tela chega em `frappe.desk.form.save.savedocs`, que recebe
    o documento como JSON no `form_dict`. Se o que está sendo salvo ali é outro
    doctype, esta OS está sendo gravada por tabela — pelo Histórico de uma
    fatura, de um pedido — e não é hora de cobrar nada de ninguém.

    Sem requisição (console, agendador, importação) também não cobramos: não há
    técnico do outro lado para preencher o campo.
    """
    bruto = (getattr(frappe.local, "form_dict", None) or {}).get("doc")
    if not bruto:
        return False

    try:
        return (frappe.parse_json(bruto) or {}).get("doctype") == doc.doctype
    except Exception:
        return False


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

    # Deixada por último de propósito: é a checagem mais cara e só importa
    # quando todas as outras já apontaram para o bloqueio.
    if not _salvando_a_propria_os(doc):
        return

    frappe.throw(
        "Preencha a <b>Quantidade Certificados</b> antes de salvar.<br><br>"
        "O conserto já foi iniciado, e é essa informação que registra quantos "
        "certificados a OS vai gerar.",
        title="Quantidade Certificados em falta",
    )
