"""Mês e ano derivados da Data de Emissão da NF, na Fatura de Venda.

São dois pares de campos, com regras diferentes de propósito:

**Mês e Ano de Emissão NF** — espelho puro. Somente leitura, recalculados a
cada save: quem manda é a data. Servem para agrupar e filtrar relatórios de
faturamento, o que a data sozinha não resolve (o Frappe não agrupa por mês a
partir de um campo Date).

**Mês e Ano da Meta** — acompanham a data enquanto a fatura é rascunho, e
depois do envio ficam livres para edição manual. É assim que uma nota emitida
no fim do mês pode ser contada na meta do mês seguinte.

O corte entre os dois momentos é automático: o `validate` roda no save e no
envio, mas não em edição de documento já enviado — lá o Frappe chama
`on_update_after_submit`, que este módulo não usa. Por isso o ajuste feito
depois do envio não é desfeito, sem precisar de nenhuma checagem de docstatus.
"""

import frappe
from frappe.utils import getdate

CAMPO_DATA = "data_de_emissao_nf"

CAMPO_MES = "mes_de_emissao_nf"
CAMPO_ANO = "ano_de_emissao_nf"

CAMPO_MES_META = "mes_da_meta"
CAMPO_ANO_META = "ano_da_meta"

# Precisa bater exatamente com as opções do Select, definidas em
# setup/custom_fields.py — o Select guarda o texto da opção, não o número.
MESES = (
    "01 - Janeiro",
    "02 - Fevereiro",
    "03 - Março",
    "04 - Abril",
    "05 - Maio",
    "06 - Junho",
    "07 - Julho",
    "08 - Agosto",
    "09 - Setembro",
    "10 - Outubro",
    "11 - Novembro",
    "12 - Dezembro",
)


def preencher_mes_ano(doc, method=None):
    data = doc.get(CAMPO_DATA)

    if not data:
        for campo in (CAMPO_MES, CAMPO_ANO, CAMPO_MES_META, CAMPO_ANO_META):
            doc.set(campo, None)
        return

    emissao = getdate(data)
    mes = MESES[emissao.month - 1]
    ano = str(emissao.year)

    for campo in (CAMPO_MES, CAMPO_MES_META):
        doc.set(campo, mes)
    for campo in (CAMPO_ANO, CAMPO_ANO_META):
        doc.set(campo, ano)
