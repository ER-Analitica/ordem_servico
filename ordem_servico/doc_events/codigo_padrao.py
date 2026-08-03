"""Reconhecimento do código de padrão — fonte única para todo o app.

Existem famílias de código diferentes conforme o tipo de padrão:

  Instrumentos      H001A03FD, L002A03TH, K001A03MU
                    (1 letra + 3 dígitos + 1 letra + 2 dígitos + 2 letras)

  Soluções padrão   26605.01, 26598.42
                    (5 dígitos + ponto + 2 dígitos — código de catálogo do
                     fabricante, ex: padrões de formazina da Hach)

Sufixos como "- T" / "- H" (termo-higrômetro, um certificado para dois canais)
são normalizados: ambos apontam para o mesmo código base.
"""

import re

# Instrumentos: H001A03FD
CODIGO_INSTRUMENTO_RE = re.compile(r"[A-Z]\d{3}[A-Z]\d{2}[A-Z]{2}")
# Soluções padrão: 26605.01 (exige início da linha/campo para não pegar medições)
CODIGO_SOLUCAO_RE = re.compile(r"^\s*(\d{5}\.\d{2})(?!\d)")

DESCRICAO_FORMATOS = (
    "H001A03FD (instrumento) ou 26605.01 (solução padrão)"
)


# Código com o sufixo de canal, como aparece impresso (ex: "N004A03TH - T")
CODIGO_COM_SUFIXO_RE = re.compile(
    r"([A-Z]\d{3}[A-Z]\d{2}[A-Z]{2})(\s*-\s*[A-Z])?(?![A-Z0-9])"
)


def extrair_codigo(texto):
    """Devolve o código BASE do padrão (sem sufixo de canal), ou None.

    É o código usado para casar com o cadastro: o termo-higrômetro tem os
    canais "- T" e "- H" no mesmo certificado, então ambos apontam para o
    mesmo registro.
    """
    if not texto:
        return None

    achado = CODIGO_INSTRUMENTO_RE.search(texto.upper())
    if achado:
        return achado.group(0)

    achado = CODIGO_SOLUCAO_RE.match(texto)
    if achado:
        return achado.group(1)

    return None


def extrair_codigo_exibicao(texto):
    """Devolve o código COMO APARECE no certificado, com sufixo de canal.

    Usado para espelhar a tabela do certificado fielmente (ex: "N004A03TH - T"
    e "N004A03TH - H" viram duas linhas distintas).
    """
    if not texto:
        return None

    achado = CODIGO_COM_SUFIXO_RE.search(texto.upper())
    if achado:
        base, sufixo = achado.group(1), achado.group(2)
        if sufixo:
            return "{} - {}".format(base, sufixo.strip(" -"))
        return base

    achado = CODIGO_SOLUCAO_RE.match(texto)
    if achado:
        return achado.group(1)

    return None


def codigo_valido(codigo):
    """True se o valor é exatamente um código de padrão válido."""
    if not codigo:
        return False
    limpo = codigo.strip()
    return bool(
        CODIGO_INSTRUMENTO_RE.fullmatch(limpo.upper())
        or CODIGO_SOLUCAO_RE.fullmatch(limpo)
    )


def codigo_do_nome_de_arquivo(file_name):
    """Código a partir do nome do arquivo: tudo antes do primeiro ' - '.

    Regra estrutural, independente do formato do código — funciona igual para
    H001A03FD, 26605.01, MR3, MRC1 ou qualquer família futura, desde que o
    arquivo siga o padrão <CÓDIGO> - <Descrição> - Val. dd-mm-aaaa.
    """
    import re as _re

    nome = _re.sub(r"\.pdf$", "", file_name or "", flags=_re.I).strip()
    if not nome:
        return None

    partes = _re.split(r"\s+-\s+", nome, maxsplit=1)
    codigo = partes[0].strip()
    # Um código não tem espaço interno nem parece uma data
    if not codigo or _re.search(r"\d{2}[-/]\d{2}[-/]\d{4}", codigo):
        return None
    return codigo


def codigos_cadastrados():
    """Códigos já cadastrados em 'Padrao de Calibracao' (o vocabulário).

    Usado para reconhecer, no certificado, códigos de qualquer formato — sem
    depender de regex. Cadastrar um padrão novo passa a ser suficiente para o
    sistema reconhecê-lo, mesmo em famílias de código ainda não previstas.
    """
    import frappe

    valores = frappe.get_all("Padrao de Calibracao", pluck="codigo")
    # Mais longos primeiro: evita casar "MR3" quando a linha traz "MR33"
    return sorted({(v or "").strip() for v in valores if v}, key=len, reverse=True)


def achar_codigo_conhecido(texto, conhecidos):
    """Procura na linha algum código já cadastrado, respeitando limites."""
    if not texto or not conhecidos:
        return None

    alvo = texto.upper()
    for codigo in conhecidos:
        padrao = r"(?<![A-Z0-9]){}(?![A-Z0-9])".format(re.escape(codigo.upper()))
        if re.search(padrao, alvo):
            return codigo
    return None
