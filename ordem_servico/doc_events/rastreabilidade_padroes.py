"""Extração da rastreabilidade dos padrões a partir do certificado anexado.

Lê a seção 5 ("Rastreabilidade dos Padrões") do PDF do certificado da OS,
extrai CÓDIGO + VALIDADE de cada padrão e localiza o registro correspondente
no doctype "Padrao de Calibracao". O vínculo é congelado na tabela filha da OS.

Funciona para Ordem Servico Interna e Ordem Servico Externa.
"""

import re

import frappe
from frappe.utils import getdate

from ordem_servico.doc_events.codigo_padrao import (
    achar_codigo_conhecido,
    codigos_cadastrados,
    extrair_codigo,
    extrair_codigo_exibicao,
)

# Datas dd/mm/aaaa ou dd-mm-aaaa
DATA_RE = re.compile(r"(\d{2})[/-](\d{2})[/-](\d{4})")
# Datas por extenso na linha, para localizar onde termina o nº do certificado
DATA_BRUTA_RE = re.compile(r"\d{2}[/-]\d{2}[/-]\d{4}")


def _para_data(match):
    d, m, y = match
    try:
        return getdate(f"{y}-{m}-{d}")
    except Exception:
        return None


def _caminho_pdf(file_url):
    achado = frappe.get_all("File", filters={"file_url": file_url}, fields=["name"], limit=1)
    if not achado:
        return None
    return frappe.get_doc("File", achado[0].name).get_full_path()


def _linhas_do_pdf(file_url):
    """Reconstrói as linhas VISUAIS da tabela agrupando fragmentos por coordenada.

    Os certificados são gerados a partir de Excel com posicionamento absoluto:
    a extração linear de texto embaralha as células (o código fica numa linha e
    as datas em outra). Agrupar por coordenada Y devolve a linha como ela aparece
    impressa, com código, certificado e datas juntos.
    """
    from collections import defaultdict

    from pypdf import PdfReader

    caminho = _caminho_pdf(file_url)
    if not caminho:
        return []

    linhas = []
    try:
        reader = PdfReader(caminho)
    except Exception:
        # Arquivo ausente no disco, corrompido ou que não é PDF: a OS fica
        # sem rastreabilidade e é sinalizada, mas nada quebra.
        return []

    for pagina in reader.pages:
        fragmentos = []

        def visitor(text, cm, tm, font_dict, font_size):
            texto = (text or "").strip()
            # Blocos multi-linha não têm coordenada confiável por linha;
            # as células da tabela vêm como fragmentos de uma linha só.
            if not texto or "\n" in texto:
                return
            fragmentos.append((round(tm[5]), tm[4], texto))

        try:
            pagina.extract_text(visitor_text=visitor)
        except Exception:
            continue

        agrupado = defaultdict(list)
        for y, x, texto in fragmentos:
            chave = next((k for k in agrupado if abs(k - y) <= 2), y)
            agrupado[chave].append((x, texto))

        # Y crescente = ordem impressa neste gerador de PDF (verificado nos
        # três layouts de certificado usados pelo laboratório).
        for y in sorted(agrupado):
            linhas.append(" ".join(t for _, t in sorted(agrupado[y])))

    return linhas


def _numero_certificado(linha):
    """Nº do certificado do padrão: o último token antes da 1ª data da linha.

    O formato varia por laboratório (026780_01, 155480, 545/2025, R1045/25),
    então a posição é mais confiável que um padrão fixo.
    """
    m = DATA_BRUTA_RE.search(linha)
    if not m:
        return ""
    antes = linha[: m.start()].split()
    return antes[-1] if antes else ""


def _parse_secao5(linhas, conhecidos=None):
    """Extrai os padrões citados na seção de rastreabilidade do certificado.

    Espelha o certificado: devolve UMA entrada por linha impressa, na mesma
    ordem e preservando códigos repetidos (ex: o termo-higrômetro aparece como
    "- T" e "- H", duas linhas apontando para o mesmo registro).

    Retorna (padroes, suspeitas):
      padroes  -> [{"codigo", "codigo_base", "cert", "validade"}]
      suspeitas-> nº de linhas com 2+ datas (cara de linha de padrão) sem código
    """
    padroes = []
    vistos = set()
    suspeitas = 0

    for linha in linhas:
        # 1) Vocabulário: reconhece qualquer código já cadastrado, de qualquer
        #    formato (MR3, MRC1, ...). 2) Regex: cobre os ainda não cadastrados.
        codigo_base = achar_codigo_conhecido(linha, conhecidos) or extrair_codigo(linha)
        datas = DATA_RE.findall(linha)

        if codigo_base:
            exibicao = extrair_codigo_exibicao(linha) or codigo_base
            validade = _para_data(datas[-1]) if datas else None
            # Evita repetir a MESMA linha (código de exibição + validade),
            # mas mantém canais distintos do mesmo instrumento.
            chave = (exibicao, validade)
            if chave in vistos:
                continue
            vistos.add(chave)
            padroes.append({
                "codigo": exibicao,
                "codigo_base": codigo_base,
                "cert": _numero_certificado(linha),
                "validade": validade,
            })
        elif len(datas) >= 2:
            suspeitas += 1

    return padroes, suspeitas


def _buscar_padrao(codigo, validade, cal_date):
    """Localiza o registro em 'Padrao de Calibracao'.

    Só vincula no casamento EXATO (código + validade do certificado): qualquer
    outra versão do mesmo código é outro documento e não pode ser vinculada.

    Retorna (registro|None, status).
    """
    campos = ["name", "codigo", "descricao", "validade", "arquivo"]
    existe_codigo = frappe.db.exists("Padrao de Calibracao", {"codigo": codigo})

    # Validade não extraída do certificado: não dá para comparar nada
    if not validade:
        return None, "Validade não lida"

    exato = frappe.get_all(
        "Padrao de Calibracao",
        filters={"codigo": codigo, "validade": validade},
        fields=campos,
        limit=1,
    )
    if exato:
        registro = exato[0]
        # Confere se o padrão estava válido na data da calibração da OS
        if cal_date and getdate(cal_date) > getdate(registro.validade):
            return registro, "Validade não cobre a data"
        return registro, "Vinculado"

    # Código cadastrado, mas com outra validade → é outro documento
    if existe_codigo:
        return None, "Validade divergente"
    return None, "Não cadastrado"


def _gravar_tabela(doctype, name, linhas, tem_alerta):
    """Escreve a tabela filha direto no banco (sem rodar validate da OS)."""
    frappe.db.delete(
        "Rastreabilidade Padrao OS",
        {"parent": name, "parenttype": doctype, "parentfield": "rastreabilidade_padroes"},
    )
    for i, row in enumerate(linhas, start=1):
        child = frappe.new_doc("Rastreabilidade Padrao OS")
        child.update(row)
        child.parent = name
        child.parenttype = doctype
        child.parentfield = "rastreabilidade_padroes"
        child.idx = i
        child.db_insert()

    frappe.db.set_value(
        doctype, name, "rastreabilidade_alerta", 1 if tem_alerta else 0, update_modified=False
    )

    # As linhas foram gravadas direto no banco (db_insert), fora do ciclo do
    # documento: sem limpar o cache, o formulário continua exibindo a versão
    # anterior (tabela vazia).
    frappe.clear_document_cache(doctype, name)


@frappe.whitelist()
def extrair_rastreabilidade(doctype, name):
    doc = frappe.get_doc(doctype, name)
    anexos = [a.strip() for a in (doc.get("anexo_certificado") or "").split("\n") if a.strip()]
    if not anexos:
        return {"ok": False, "motivo": "sem_certificado"}

    padroes = []
    suspeitas = 0
    algum_com_texto = False
    vistos = set()

    conhecidos = codigos_cadastrados()

    for url in anexos:
        linhas = _linhas_do_pdf(url)
        if any(l.strip() for l in linhas):
            algum_com_texto = True
        encontrados, susp = _parse_secao5(linhas, conhecidos)
        for info in encontrados:
            chave = (info["codigo"], info["validade"])
            if chave in vistos:
                continue
            vistos.add(chave)
            padroes.append(info)
        suspeitas += susp

    if not algum_com_texto:
        return {"ok": False, "motivo": "pdf_sem_texto"}

    cal_date = doc.get("data_cal")
    linhas_tabela = []
    tem_alerta = suspeitas > 0
    pendentes = []

    # Mantém a ordem em que os padrões aparecem no certificado (espelhamento)
    for info in padroes:
        codigo = info["codigo"]
        validade = info.get("validade")
        registro, status = _buscar_padrao(info["codigo_base"], validade, cal_date)

        row = {
            "codigo": codigo,
            "certificado_padrao": info.get("cert") or "",
            "validade": str(validade) if validade else "",
            "status": status,
        }

        if registro:
            row["descricao"] = registro.get("descricao") or ""
            row["padrao"] = registro.get("name")
            row["arquivo_padrao"] = registro.get("arquivo") or ""
        else:
            row["descricao"] = ""
            row["padrao"] = ""
            row["arquivo_padrao"] = ""
            pendentes.append({
                "codigo": codigo,
                "validade": str(validade) if validade else "",
                "status": status,
            })

        if status != "Vinculado":
            tem_alerta = True

        linhas_tabela.append(row)

    _gravar_tabela(doctype, name, linhas_tabela, tem_alerta)

    return {
        "ok": True,
        "padroes": len(linhas_tabela),
        "suspeitas": suspeitas,
        "alerta": tem_alerta,
        "pendentes": pendentes,
    }


def on_update(doc, method=None):
    """Repovoa a rastreabilidade quando a OS é salva sem a tabela preenchida.

    Ao salvar, o Frappe reescreve as tabelas filhas com o que veio do
    formulário. Como as linhas são gravadas fora do ciclo do documento (para
    não disparar as validações da OS), um save feito com a tela desatualizada
    apagaria tudo. Este gancho reconstrói automaticamente nesse caso.
    """
    if not doc.get("anexo_certificado"):
        return
    if doc.get("rastreabilidade_padroes"):
        return

    try:
        extrair_rastreabilidade(doc.doctype, doc.name)
    except Exception:
        frappe.log_error(
            title="Falha ao repovoar rastreabilidade de padrões",
            message=frappe.get_traceback(),
        )


# Quem recebe o aviso de rastreabilidade pendente no desk.
# Para incluir alguém, basta acrescentar o e-mail (login) nesta lista.
USUARIOS_AVISO_RASTREABILIDADE = (
    "assistencia@eranalitica.com.br",
    "lucas.campos@eranalitica.com.br",
    "admin@example.com",
)


def _pode_ver_aviso():
    """Aceita tanto o login quanto o e-mail cadastrado do usuário.

    O Frappe identifica o usuário pelo login, que nem sempre é o e-mail —
    o Administrator, por exemplo, faz login como "Administrator" mas tem
    "admin@example.com" no cadastro.
    """
    usuario = frappe.session.user
    if usuario in USUARIOS_AVISO_RASTREABILIDADE:
        return True

    email = frappe.db.get_value("User", usuario, "email")
    return bool(email and email in USUARIOS_AVISO_RASTREABILIDADE)


@frappe.whitelist()
def contar_alertas():
    """Quantas OS estão com pendência de rastreabilidade (para a barra do desk).

    O aviso é dirigido a quem cuida da rastreabilidade; para os demais
    usuários a contagem volta zerada e a barra não aparece.
    """
    if not _pode_ver_aviso():
        return {"interna": 0, "externa": 0}

    resultado = {}
    for doctype, chave in (
        ("Ordem Servico Interna", "interna"),
        ("Ordem Servico Externa", "externa"),
    ):
        try:
            resultado[chave] = frappe.db.count(doctype, {"rastreabilidade_alerta": 1})
        except Exception:
            resultado[chave] = 0
    return resultado


@frappe.whitelist()
def revincular_em_lote(doctype, nomes=None, escopo="selecionadas", limite=300):
    """Reprocessa a rastreabilidade de várias OS de uma vez.

    escopo:
      selecionadas -> apenas as OS informadas em `nomes`
      pendentes    -> OS com certificado e alerta de rastreabilidade
      sem_tabela   -> OS com certificado que ainda não têm a tabela preenchida
    """
    import json

    if isinstance(nomes, str):
        nomes = json.loads(nomes)

    if escopo == "selecionadas":
        alvos = list(nomes or [])
    else:
        filtros = {"anexo_certificado": ["is", "set"]}
        if escopo == "pendentes":
            filtros["rastreabilidade_alerta"] = 1
        alvos = frappe.get_all(
            doctype, filters=filtros, pluck="name", limit_page_length=int(limite)
        )
        if escopo == "sem_tabela":
            com_tabela = set(
                frappe.get_all(
                    "Rastreabilidade Padrao OS",
                    filters={"parenttype": doctype, "parent": ["in", alvos]},
                    pluck="parent",
                )
            ) if alvos else set()
            alvos = [n for n in alvos if n not in com_tabela]

    processadas, com_alerta, erros = 0, 0, []

    for nome in alvos:
        try:
            res = extrair_rastreabilidade(doctype, nome)
            if res.get("ok"):
                processadas += 1
                if res.get("alerta"):
                    com_alerta += 1
            else:
                erros.append({"os": nome, "motivo": res.get("motivo")})
        except Exception:
            erros.append({"os": nome, "motivo": "erro inesperado"})
            frappe.log_error(
                title="Falha ao revincular padrões em lote",
                message=frappe.get_traceback(),
            )

    frappe.db.commit()
    return {
        "total": len(alvos),
        "processadas": processadas,
        "com_alerta": com_alerta,
        "erros": erros[:20],
    }


@frappe.whitelist()
def cadastrar_padrao_e_revincular(doctype, name, codigo, descricao, validade, arquivo):
    """Cadastra o padrão faltante e já refaz o vínculo na OS."""
    codigo = (codigo or "").strip().upper()
    if not codigo or not validade or not arquivo:
        frappe.throw("Preencha código, validade e anexe o arquivo do padrão.")

    if frappe.db.exists("Padrao de Calibracao", {"codigo": codigo, "validade": validade}):
        frappe.throw("Já existe um padrão cadastrado com esse código e validade.")

    padrao = frappe.new_doc("Padrao de Calibracao")
    padrao.codigo = codigo
    padrao.descricao = (descricao or "").strip()
    padrao.validade = validade
    padrao.arquivo = arquivo
    padrao.insert()

    resultado = extrair_rastreabilidade(doctype, name)
    return {"padrao": padrao.name, "rastreabilidade": resultado}
