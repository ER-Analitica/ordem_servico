"""Importação em massa de Padrões de Calibração a partir da pasta de arquivos.

Toda a informação vem do NOME DO ARQUIVO, no formato:
    <CÓDIGO> - <Descrição> - Val. dd-mm-aaaa.pdf
Ex: "H001A03FD - Filtro de Óxido de Holmio - Val. 03-11-2027.pdf"

Arquivos fora do padrão não são cadastrados: voltam numa lista com o motivo,
para correção assistida na própria tela de importação.
"""

import re

import frappe
from frappe.utils import getdate

# Pasta-raiz dos padrões (subpastas por ano dentro dela)
PASTA_PADROES = "Home/Padrões"

from ordem_servico.doc_events.codigo_padrao import codigo_do_nome_de_arquivo, codigo_valido

# Data completa dd-mm-aaaa ou dd/mm/aaaa
DATA_COMPLETA_RE = re.compile(r"(\d{2})[-/](\d{2})[-/](\d{4})")
# Ano solto (para detectar "Val. 2027" e orientar a correção)
ANO_RE = re.compile(r"\b(20\d{2})\b")


def _pasta_do_ano(ano):
    """Pasta dos padrões em uso naquele ano: Home/Padrões/AAAA."""
    return "{}/{}".format(PASTA_PADROES, ano)


def _arquivos_da_pasta(ano):
    pasta = _pasta_do_ano(ano)
    return frappe.get_all(
        "File",
        filters={"is_folder": 0},
        or_filters=[
            ["folder", "=", pasta],
            ["folder", "like", pasta + "/%"],
        ],
        fields=["file_name", "file_url", "folder"],
    )


def analisar_nome(file_name):
    """Extrai codigo/descricao/validade do nome. Retorna (dados, erro)."""
    nome = re.sub(r"\.pdf$", "", file_name or "", flags=re.I).strip()

    dados = {"codigo": "", "descricao": "", "validade": ""}

    # --- Código: tudo antes do primeiro " - " (regra estrutural, serve para
    #     qualquer família de código: H001A03FD, 26605.01, MR3, MRC1, ...) ---
    codigo = codigo_do_nome_de_arquivo(file_name)
    if not codigo:
        return dados, (
            "Não foi possível ler o código no início do nome. "
            "Esperado <b>Código - Descrição - Val. dd-mm-aaaa</b>."
        )
    dados["codigo"] = codigo

    # --- Validade (após "Val.") ---
    partes = re.split(r"\bval\.?\s*", nome, flags=re.I)
    trecho_validade = partes[-1] if len(partes) > 1 else ""

    m_data = DATA_COMPLETA_RE.search(trecho_validade)
    if m_data:
        d, mth, y = m_data.groups()
        try:
            dados["validade"] = str(getdate(f"{y}-{mth}-{d}"))
        except Exception:
            return dados, f"Data de validade inválida: '{m_data.group(0)}'."
    else:
        anos = ANO_RE.findall(trecho_validade or nome)
        if anos:
            return dados, (
                f"Data incompleta (encontrado apenas o ano {anos[-1]}). "
                "Renomeie para o formato <b>Val. dd-mm-aaaa</b>."
            )
        return dados, "Sem data de validade no nome (esperado <b>Val. dd-mm-aaaa</b>)."

    # --- Descrição (entre o código e o "Val.") ---
    pos = nome.upper().find(dados["codigo"].upper())
    miolo = nome[pos + len(dados["codigo"]):] if pos >= 0 else nome
    miolo = re.split(r"\bval\.?\s*", miolo, flags=re.I)[0]
    dados["descricao"] = miolo.strip(" -–—\t").strip()
    if not dados["descricao"]:
        return dados, "Sem descrição no nome (esperado <b>Código - Descrição - Val. data</b>)."

    return dados, None


def _ja_existe(codigo, validade):
    return frappe.db.exists(
        "Padrao de Calibracao", {"codigo": codigo, "validade": validade}
    )


def _criar(codigo, descricao, validade, file_url):
    doc = frappe.new_doc("Padrao de Calibracao")
    doc.codigo = codigo
    doc.descricao = descricao
    doc.validade = validade
    doc.arquivo = file_url
    doc.insert()
    return doc.name


@frappe.whitelist()
def importar_padroes(ano=None):
    """Varre a pasta do ano informado (padrão: ano atual) e cadastra os
    padrões cujo nome está no formato correto."""
    ano = str(ano or frappe.utils.nowdate()[:4])
    arquivos = _arquivos_da_pasta(ano)
    if not arquivos:
        return {
            "ano": ano,
            "pasta": _pasta_do_ano(ano),
            "total": 0,
            "criados": [],
            "ignorados": [],
            "falhas": [],
        }

    criados, ignorados, conferir, falhas = [], [], [], []

    for arq in arquivos:
        file_name = arq.get("file_name")
        file_url = arq.get("file_url")

        def _registro(motivo):
            return {
                "file_name": file_name,
                "file_url": file_url,
                "folder": arq.get("folder"),
                "motivo": motivo,
                "codigo": dados.get("codigo") or "",
                "descricao": dados.get("descricao") or "",
                "validade": dados.get("validade") or "",
            }

        dados, erro = analisar_nome(file_name)
        if erro:
            falhas.append(_registro(erro))
            continue

        if _ja_existe(dados["codigo"], dados["validade"]):
            ignorados.append({"file_name": file_name, "codigo": dados["codigo"]})
            continue

        # Só cadastra sozinho os formatos de código consolidados. Famílias
        # fora do padrão conhecido (ex: "MRC1 - F1000") vão para conferência:
        # o código é a chave de todo o casamento, não pode ser adivinhado.
        if not codigo_valido(dados["codigo"]):
            conferir.append(_registro(
                "Formato de código fora do padrão conhecido — confira o código antes de cadastrar."
            ))
            continue

        try:
            name = _criar(dados["codigo"], dados["descricao"], dados["validade"], file_url)
            criados.append({"name": name, "file_name": file_name, "codigo": dados["codigo"]})
        except Exception as e:
            falhas.append(_registro(str(e)))

    return {
        "ano": ano,
        "pasta": _pasta_do_ano(ano),
        "total": len(arquivos),
        "criados": criados,
        "ignorados": ignorados,
        "conferir": conferir,
        "falhas": falhas,
    }


@frappe.whitelist()
def importar_corrigido(codigo, descricao, validade, file_url):
    """Cadastra um padrão a partir dos dados corrigidos na tela de importação."""
    codigo = (codigo or "").strip().upper()
    descricao = (descricao or "").strip()

    if not codigo or not validade or not file_url:
        frappe.throw("Preencha código, validade e mantenha o arquivo selecionado.")

    if _ja_existe(codigo, validade):
        return {"ok": False, "motivo": "Já existe um padrão com esse código e validade."}

    name = _criar(codigo, descricao, validade, file_url)
    return {"ok": True, "name": name}
