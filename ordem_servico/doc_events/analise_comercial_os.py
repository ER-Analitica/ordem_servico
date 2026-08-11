"""Espelha a Análise Comercial do Pedido de Venda nas Ordens de Serviço.

Este módulo cuida da propagação: quando a análise muda no pedido, as OS que o
mostram no Histórico são atualizadas.

O caminho inverso — descobrir de qual pedido cada OS deve ler — fica em
`historico_pedido`, junto com o resto do Histórico.
"""

import frappe

# Campos espelhados: {campo no Pedido: campo na OS}.
# Quase todos têm o mesmo nome; a exceção é o "tipo", que na OS virou
# "tipo_confirmacao" — o nome genérico colidia com um Property Setter antigo
# do sistema que forçava o campo a ficar oculto.
MAPA_CAMPOS = {
    "data_limite_de_faturamento": "data_limite_de_faturamento",
    "tipo_de_faturamento": "tipo_de_faturamento",
    "faturamento_parcial": "faturamento_parcial",
    "confirmacao_do_cliente": "confirmacao_do_cliente",
    "tipo": "tipo_confirmacao",
    "confirmacao": "confirmacao",
}

CAMPOS_PEDIDO = tuple(MAPA_CAMPOS.keys())

DOCTYPES_OS = ("Ordem Servico Interna", "Ordem Servico Externa")

# Campos que o Pedido só mostra quando o cliente confirmou — lá eles têm
# `depends_on: doc.confirmacao_do_cliente == 'SIM'`. O valor continua gravado
# quando a confirmação volta para "NÃO", então espelhar sem repetir a regra
# faria a OS exibir um dado que o próprio pedido esconde.
CAMPOS_SO_COM_CONFIRMACAO = ("tipo", "confirmacao")


def valores_espelhados(origem):
    """Análise Comercial a gravar na OS, no formato {campo da OS: valor}.

    `origem` pode ser o documento do Pedido ou uma linha lida do banco.
    """
    confirmado = (origem.get("confirmacao_do_cliente") or "").strip().upper() == "SIM"

    return {
        campo_os: (
            None
            if campo_pedido in CAMPOS_SO_COM_CONFIRMACAO and not confirmado
            else origem.get(campo_pedido)
        )
        for campo_pedido, campo_os in MAPA_CAMPOS.items()
    }


def _analise_mudou(doc):
    anterior = doc.get_doc_before_save()
    if not anterior:
        return True  # pedido novo
    return any(doc.get(c) != anterior.get(c) for c in CAMPOS_PEDIDO)


def propagar_do_pedido(doc, method=None):
    """Gatilho no Pedido — atualiza as OS que o exibem no Histórico.

    A busca é pelo `sales_order_name` (o campo do Histórico) porque é ele que
    aponta para o pedido vigente; o vínculo digitado pelo usuário pode estar
    numa versão anterior da cadeia de retificações.

    A gravação é um UPDATE por doctype, não um save por OS: um pedido chega a
    ter centenas de OS, e rodar as validações de todas deixaria o processo
    lento — pior, uma OS com pendência poderia abortar o salvamento do pedido.
    """
    if not _analise_mudou(doc):
        return

    espelho = valores_espelhados(doc)
    campos_os = tuple(espelho.keys())
    valores = [espelho[c] for c in campos_os]
    atribuicoes = ", ".join("`{}` = %s".format(c) for c in campos_os)

    for doctype in DOCTYPES_OS:
        tabela = "tab{}".format(doctype)

        # Nomes das OS afetadas: precisamos deles para limpar o cache do
        # documento — sem isso um formulário aberto continuaria com os valores
        # antigos e poderia gravá-los de volta ao ser salvo.
        afetadas = frappe.db.sql(
            "SELECT name FROM `{}` WHERE `sales_order_name` = %s".format(tabela),
            [doc.name],
            pluck="name",
        )
        if not afetadas:
            continue

        frappe.db.sql(
            "UPDATE `{}` SET {} WHERE `sales_order_name` = %s".format(
                tabela, atribuicoes
            ),
            valores + [doc.name],
        )

        for nome in afetadas:
            frappe.clear_document_cache(doctype, nome)
