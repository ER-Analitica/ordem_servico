"""Mantém o Histórico da OS apontando para o pedido que está valendo.

Regra do negócio:

* O vínculo digitado pelo usuário — "Pedido de Venda Referência" na OS Externa
  e "Possui Pedido de Venda" na OS Interna — **nunca** é alterado por código.
  Ele registra o que a pessoa escolheu e assim continua.

* O **Histórico** é derivado desse vínculo: ele mostra o pedido vigente. Se o
  pedido foi cancelado e retificado (SO-XXXX vira SO-XXXX-1, um documento
  novo), o Histórico acompanha a retificação. Se foi cancelado sem
  retificação, o Histórico esvazia — não existe pedido válido para mostrar.

* Data do Pedido, Orçamento, Data do Orçamento e a Análise Comercial saem
  todos do pedido do Histórico, e por isso acompanham essas mudanças.
"""

import re

import frappe

from ordem_servico.doc_events import pontos_calibracao_os
from ordem_servico.doc_events.analise_comercial_os import (
    MAPA_CAMPOS,
    valores_espelhados,
)

# Sufixo que o Frappe acrescenta ao retificar: SO-03373 vira SO-03373-1,
# depois SO-03373-2, e assim por diante.
SUFIXO_RETIFICACAO = re.compile(r"-\d+$")

# Campo onde cada OS guarda o vínculo escolhido pelo usuário.
LINK_USUARIO = {
    "Ordem Servico Interna": "has_sales_order_link",
    "Ordem Servico Externa": "sales_order_reference",
}

# OS em que uma alteração dos Pontos de Calibração no pedido substitui o que
# estiver na OS, mesmo que alguém tenha editado ali.
PEDIDO_TEM_PRIORIDADE = ("Ordem Servico Externa",)

# Campos do Histórico derivados do pedido.
CAMPOS_HISTORICO = (
    "sales_order_name",
    "sales_order_date",
    "quotation_name",
    "quotation_date",
    "obs_historico",
)

# Tudo que este módulo recalcula: Histórico + Análise Comercial.
CAMPOS_DERIVADOS = CAMPOS_HISTORICO + tuple(MAPA_CAMPOS.values())

VAZIO = {campo: None for campo in CAMPOS_DERIVADOS}


def _cadeia(doctype, nome):
    """Cadeia de retificações à qual `nome` pertence, da raiz à última versão.

    Retorna [(nome, docstatus), ...]. Uma cadeia pode ser longa — há pedidos
    aqui com mais de 40 versões — e isso é consultado a cada save de OS, então
    a busca traz o bloco inteiro de uma vez pelo padrão do nome e só monta a
    ordem em memória, usando o `amended_from` como fonte da verdade.
    """
    nome = (nome or "").strip()
    if not nome:
        return []

    proprio = frappe.db.get_value(
        doctype, nome, ["name", "amended_from", "docstatus"], as_dict=True
    )
    if not proprio:
        return []  # documento apagado

    # O nome da raiz é o prefixo comum de toda a cadeia. Só dá para remover o
    # sufixo quando o documento é comprovadamente uma retificação: nomes como
    # "SO-03378" também terminam em traço e dígitos, e recortá-los deixaria só
    # "SO" — um prefixo que varreria a tabela inteira.
    base = SUFIXO_RETIFICACAO.sub("", nome) if proprio.amended_from else nome

    # SQL direto em vez de frappe.get_all: isto roda a cada save de OS e a
    # checagem de permissão do ORM custa mais que a consulta em si.
    candidatos = {
        d.name: d
        for d in frappe.db.sql(
            "SELECT name, amended_from, docstatus FROM `tab{}` "
            "WHERE name = %s OR name LIKE %s".format(doctype),
            (base, "{}-%".format(base)),
            as_dict=True,
        )
    }
    candidatos.setdefault(nome, proprio)

    sucessor_de = {
        d.amended_from: d.name for d in candidatos.values() if d.amended_from
    }

    raiz = nome
    vistos = set()
    while raiz not in vistos:
        vistos.add(raiz)
        anterior = (candidatos.get(raiz) or {}).get("amended_from")
        if not anterior or anterior not in candidatos:
            break
        raiz = anterior

    ordenada = [raiz]
    while True:
        ultimo = ordenada[-1]
        proximo = sucessor_de.get(ultimo)

        if not proximo and (candidatos.get(ultimo) or {}).get("docstatus") == 2:
            # Documento cancelado e sem sucessor no bloco lido. Só aqui vale
            # confirmar no banco (a coluna amended_from não é indexada, então
            # a consulta varre a tabela): se a retificação tiver fugido do
            # padrão de nome, é isto que a encontra.
            proximo = frappe.db.get_value(doctype, {"amended_from": ultimo}, "name")
            if proximo and proximo not in candidatos:
                candidatos[proximo] = frappe.db.get_value(
                    doctype, proximo, ["name", "amended_from", "docstatus"], as_dict=True
                )

        if not proximo or proximo in ordenada:
            break
        ordenada.append(proximo)

    return [(n, candidatos[n]["docstatus"]) for n in ordenada if n in candidatos]


def resolver(doctype, nome):
    """Documento da cadeia a ser exibido no Histórico.

    Retorna (documento, cancelado_sem_retificacao).

    Quando a cadeia inteira está cancelada não existe substituto, e apagar o
    Histórico esconderia a única pista do que aconteceu. Nesse caso fica o
    último documento da cadeia, sinalizado — quem abrir a OS vê o pedido
    cancelado e a observação explicando.
    """
    cadeia = _cadeia(doctype, nome)
    if not cadeia:
        return None, False  # documento apagado

    # Só interessa o que vem de `nome` em diante: versões anteriores já foram
    # substituídas.
    nome = (nome or "").strip()
    posicao = next((i for i, (n, _) in enumerate(cadeia) if n == nome), 0)
    trecho = cadeia[posicao:]

    for candidato, docstatus in trecho:
        if docstatus != 2:  # rascunho ou enviado
            return candidato, False

    return trecho[-1][0], True


def documento_vigente(doctype, nome):
    """Documento da cadeia que está valendo, ou None se todos cancelados."""
    documento, cancelado = resolver(doctype, nome)
    return None if cancelado else documento


def familia(doctype, nome):
    """Todos os documentos da cadeia de retificações à qual `nome` pertence.

    Uma OS pode ter sido vinculada a qualquer versão da cadeia, então ao
    cancelar ou retificar precisamos alcançar todas elas.
    """
    return [n for n, _ in _cadeia(doctype, nome)]


def valores_derivados(pedido_escolhido):
    """Valores do Histórico e da Análise Comercial para um vínculo do usuário."""
    nome_pedido, pedido_cancelado = resolver("Sales Order", pedido_escolhido)
    if not nome_pedido:
        return dict(VAZIO)

    pedido = frappe.db.get_value(
        "Sales Order",
        nome_pedido,
        ["transaction_date", "quotation_name"] + list(MAPA_CAMPOS.keys()),
        as_dict=True,
    )

    # O orçamento também pode ter sido retificado.
    nome_orcamento, orcamento_cancelado = resolver("Quotation", pedido.quotation_name)

    observacoes = []
    if pedido_cancelado:
        observacoes.append(
            "Pedido de Venda {} cancelado, sem retificação. "
            "O Histórico e a Análise Comercial são deste pedido.".format(nome_pedido)
        )
    if orcamento_cancelado:
        observacoes.append(
            "Orçamento {} cancelado, sem retificação.".format(nome_orcamento)
        )

    valores = {
        "sales_order_name": nome_pedido,
        "sales_order_date": pedido.transaction_date,
        "quotation_name": nome_orcamento,
        "quotation_date": (
            frappe.db.get_value("Quotation", nome_orcamento, "transaction_date")
            if nome_orcamento
            else None
        ),
        "obs_historico": "\n".join(observacoes) or None,
    }
    valores.update(valores_espelhados(pedido))

    return valores


def _origem(doc):
    """De onde parte a busca pelo pedido vigente."""
    manual = (doc.get(LINK_USUARIO.get(doc.doctype, "")) or "").strip()
    if manual:
        return manual

    # OS antigas, criadas antes dos campos de vínculo: o único registro do
    # pedido está no próprio Histórico.
    return (doc.get("sales_order_name") or "").strip()


def aplicar_na_os(doc, method=None):
    """Gatilho no validate das OS — refaz o Histórico e a Análise Comercial."""
    origem = _origem(doc)
    if not origem:
        return

    for campo, valor in valores_derivados(origem).items():
        doc.set(campo, valor)


# --------------------------------------------------------------------------
# Propagação: cancelamento e retificação do Pedido ou do Orçamento
# --------------------------------------------------------------------------


def _regravar(doctype, nomes_os):
    """Recalcula os campos derivados de um conjunto de OS já salvas.

    Grava direto na tabela em vez de dar save em cada OS: um pedido chega a ter
    centenas de OS, e rodar as validações de todas deixaria o cancelamento
    lento — pior, uma OS com pendência poderia abortar a operação.
    """
    if not nomes_os:
        return

    campo_link = LINK_USUARIO[doctype]
    tabela = "tab{}".format(doctype)
    atribuicoes = ", ".join("`{}` = %s".format(c) for c in CAMPOS_DERIVADOS)

    # OS que partem do mesmo vínculo chegam ao mesmo pedido vigente, então
    # agrupamos para calcular uma vez só e gravar em lote.
    por_origem = {}
    for nome in nomes_os:
        linha = frappe.db.get_value(
            doctype, nome, [campo_link, "sales_order_name"], as_dict=True
        )
        origem = (linha.get(campo_link) or linha.get("sales_order_name") or "").strip()
        if not origem:
            # OS sem vínculo com pedido nenhum. Ela chega aqui pelo
            # sincronizar_orcamento, que alcança as OS pelo `quotation_name` —
            # e nas OS que geraram o próprio orçamento esse campo não é
            # derivado, é escrito pelo set_quotation_history. Recalcular
            # apagaria justamente o orçamento que a OS acabou de gerar.
            continue
        por_origem.setdefault(origem, []).append(nome)

    for origem, nomes in por_origem.items():
        valores = valores_derivados(origem)
        marcadores = ", ".join(["%s"] * len(nomes))

        frappe.db.sql(
            "UPDATE `{}` SET {} WHERE name IN ({})".format(
                tabela, atribuicoes, marcadores
            ),
            [valores[c] for c in CAMPOS_DERIVADOS] + nomes,
        )

        for nome in nomes:
            frappe.clear_document_cache(doctype, nome)


def _resincronizar_pontos(doctype, nomes_os, nomes_cadeia):
    """Repassa os Pontos de Calibração após cancelamento ou retificação.

    No save comum o campo só é preenchido quando está vazio, para não desfazer
    o ajuste do técnico. Aqui é diferente: o documento de origem foi corrigido
    e os pontos precisam acompanhar.

    Na **OS Interna** ainda protegemos quem escreveu à mão: só substituímos
    onde o texto atual é o que veio de alguma versão da cadeia.

    Na **OS Externa** o pedido tem prioridade e substitui sempre. Ali os pontos
    são o que foi contratado e o que o cliente vai auditar — uma correção no
    pedido precisa chegar à OS sem depender de ninguém.
    """
    if not nomes_os or not nomes_cadeia:
        return

    herdados = {
        pontos_calibracao_os.normalizar(pontos)
        for (pontos,) in frappe.db.sql(
            "SELECT `{}` FROM `tabSales Order` WHERE name IN ({})".format(
                pontos_calibracao_os.CAMPO_ORIGEM,
                ", ".join(["%s"] * len(nomes_cadeia)),
            ),
            nomes_cadeia,
        )
    }
    herdados.discard("")

    linhas = frappe.db.sql(
        "SELECT name, `{}` AS pontos, sales_order_name, quotation_name "
        "FROM `tab{}` WHERE name IN ({})".format(
            pontos_calibracao_os.CAMPO_OS,
            doctype,
            ", ".join(["%s"] * len(nomes_os)),
        ),
        nomes_os,
        as_dict=True,
    )

    por_valor = {}
    for linha in linhas:
        atual = linha.pontos
        editado_a_mao = (
            not pontos_calibracao_os.vazio(atual)
            and pontos_calibracao_os.normalizar(atual) not in herdados
        )
        if editado_a_mao and doctype not in PEDIDO_TEM_PRIORIDADE:
            continue

        novo = pontos_calibracao_os.escolher_pontos(linha.sales_order_name)
        if pontos_calibracao_os.normalizar(novo) == pontos_calibracao_os.normalizar(atual):
            continue

        por_valor.setdefault(novo, []).append(linha.name)

    for valor, nomes in por_valor.items():
        frappe.db.sql(
            "UPDATE `tab{}` SET `{}` = %s WHERE name IN ({})".format(
                doctype,
                pontos_calibracao_os.CAMPO_OS,
                ", ".join(["%s"] * len(nomes)),
            ),
            [valor] + nomes,
        )
        for nome in nomes:
            frappe.clear_document_cache(doctype, nome)


def sincronizar_pedido(doc, method=None):
    """Gatilho no Pedido de Venda — cancelamento e retificação.

    Alcança as OS ligadas a qualquer versão da cadeia: uma OS pode apontar
    para a SO-XXXX original enquanto o que vale hoje é a SO-XXXX-3.
    """
    nomes_familia = familia("Sales Order", doc.name)
    if not nomes_familia:
        return

    for doctype, campo_link in LINK_USUARIO.items():
        nomes_os = set()
        for campo in (campo_link, "sales_order_name"):
            nomes_os.update(
                frappe.get_all(
                    doctype, filters={campo: ["in", nomes_familia]}, pluck="name"
                )
            )
        _regravar(doctype, sorted(nomes_os))
        _resincronizar_pontos(doctype, sorted(nomes_os), nomes_familia)


def sincronizar_orcamento(doc, method=None):
    """Gatilho no Orçamento — cancelamento e retificação.

    O orçamento não é o vínculo da OS: chegamos até ela pelos pedidos que
    saíram dele.
    """
    nomes_familia = familia("Quotation", doc.name)
    if not nomes_familia:
        return

    pedidos = frappe.get_all(
        "Sales Order", filters={"quotation_name": ["in", nomes_familia]}, pluck="name"
    )

    for doctype, campo_link in LINK_USUARIO.items():
        nomes_os = set(
            frappe.get_all(
                doctype, filters={"quotation_name": ["in", nomes_familia]}, pluck="name"
            )
        )
        if pedidos:
            for campo in (campo_link, "sales_order_name"):
                nomes_os.update(
                    frappe.get_all(
                        doctype, filters={campo: ["in", pedidos]}, pluck="name"
                    )
                )
        _regravar(doctype, sorted(nomes_os))
