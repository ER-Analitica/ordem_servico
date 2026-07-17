from collections import defaultdict

import frappe

from ordem_servico.doc_events.validacao_duplicidade_equipamentos import (
    normalizar,
    serie_e_generica,
)


def _contar_os_por_equipamento():
    """Quantas OS (Interna + Externa) apontam para cada equipamento."""
    contagem = defaultdict(int)
    for doctype in ("Ordem Servico Interna", "Ordem Servico Externa"):
        linhas = frappe.db.sql(
            """
            SELECT informe_numero_serie AS eq, COUNT(*) AS qtd
            FROM `tab{}`
            WHERE informe_numero_serie IS NOT NULL AND informe_numero_serie != ''
            GROUP BY informe_numero_serie
            """.format(doctype),
            as_dict=True,
        )
        for linha in linhas:
            contagem[linha.eq] += linha.qtd
    return contagem


@frappe.whitelist()
def grupos_de_duplicatas():
    """Agrupa os equipamentos suspeitos de duplicidade em 3 níveis:
    A — mesma série real no mesmo cliente (quase certeza)
    B — idênticos (equipamento/modelo/marca) sem série real, mesmo cliente
    C — mesma série real em clientes diferentes (revisar dono)
    """
    equipamentos = frappe.get_all(
        "Equipamentos",
        fields=["name", "customer", "numero_serie", "tag", "descricao",
                "modelo_equipamento", "marca_equipamento", "creation"],
    )
    os_count = _contar_os_por_equipamento()

    grupo_a = defaultdict(list)
    grupo_b = defaultdict(list)
    grupo_c = defaultdict(list)

    for eq in equipamentos:
        eq["os_count"] = os_count.get(eq["name"], 0)
        serie = normalizar(eq["numero_serie"])
        if serie_e_generica(serie):
            chave_b = (eq["customer"], eq["descricao"],
                       eq["modelo_equipamento"], eq["marca_equipamento"])
            grupo_b[chave_b].append(eq)
        else:
            grupo_a[(eq["customer"], serie)].append(eq)
            grupo_c[serie].append(eq)

    grupos = []

    for (customer, serie), itens in grupo_a.items():
        if len(itens) > 1:
            grupos.append({
                "tipo": "A",
                "titulo": "Mesma série '{}' no cliente {}".format(
                    itens[0]["numero_serie"], customer),
                "confianca": "Quase certeza de duplicata",
                "itens": _ordenar(itens),
            })

    for (customer, descricao, modelo, marca), itens in grupo_b.items():
        if len(itens) > 1:
            grupos.append({
                "tipo": "B",
                "titulo": "Idênticos sem série real — {} / {} / {} no cliente {}".format(
                    descricao, modelo, marca, customer),
                "confianca": "Provável duplicata — verificar manualmente",
                "itens": _ordenar(itens),
            })

    for serie, itens in grupo_c.items():
        clientes = {i["customer"] for i in itens}
        if len(clientes) > 1:
            grupos.append({
                "tipo": "C",
                "titulo": "Série '{}' em clientes diferentes".format(
                    itens[0]["numero_serie"]),
                "confianca": "Revisar o dono correto antes de qualquer mesclagem",
                "itens": _ordenar(itens),
            })

    ordem = {"A": 0, "B": 1, "C": 2}
    grupos.sort(key=lambda g: ordem[g["tipo"]])
    return grupos


def _ordenar(itens):
    # Sobrevivente sugerido primeiro: mais OS vinculadas e mais antigo
    return sorted(itens, key=lambda i: (-i["os_count"], str(i["creation"])))


@frappe.whitelist()
def mesclar_equipamentos(origem, destino):
    """Mescla o equipamento 'origem' dentro do 'destino'.
    Todas as OS e demais links que apontavam para a origem são
    reapontados automaticamente pelo Frappe; a origem é excluída."""
    if not frappe.has_permission("Equipamentos", "delete"):
        frappe.throw("Você não tem permissão para mesclar equipamentos "
                     "(requer permissão de exclusão em Equipamentos).")
    if origem == destino:
        frappe.throw("Origem e destino são o mesmo registro.")

    frappe.rename_doc("Equipamentos", origem, destino, merge=True, force=True)
    return destino
