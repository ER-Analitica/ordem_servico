from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

CUSTOM_FIELDS = {
    "Sales Invoice": [
        {
            # Seção que já existia recolhida. Como as informações da nota são
            # consultadas o tempo todo, ela passa a ficar sempre aberta —
            # `collapsible: 0` é o que tira a setinha do título.
            "fieldname": "informações_nota_fiscal",
            "fieldtype": "Section Break",
            "label": "Informações Nota Fiscal",
            "collapsible": 0,
            "insert_after": "update_billed_amount_in_sales_order",
        },
        # Número da NF e Data de Emissão lado a lado. No Frappe isso se faz com
        # um Column Break entre os dois campos.
        #
        # A quebra vem depois do `amended_from` de propósito: os nativos que
        # caem nesta seção (Is Rate Adjustment Entry e Alterado De) ficam entre
        # o número e a quebra, ou seja, na coluna da esquerda, abaixo do Número
        # da NF. Assim a direita fica só com a data e nenhum espaço sobra.
        {
            "fieldname": "cb_nota_fiscal",
            "fieldtype": "Column Break",
            "insert_after": "amended_from",
        },
        {
            # Campo já existente: só muda de lugar, para o outro lado da coluna.
            "fieldname": "data_de_emissao_nf",
            "fieldtype": "Date",
            "label": "Data de Emissão NF",
            "insert_after": "cb_nota_fiscal",
        },
        # Mês e ano da emissão, derivados da data acima para agrupar e filtrar
        # relatórios. São somente leitura: preenchidos por
        # doc_events/mes_ano_emissao_nf.py a cada save.
        {
            # O número vem antes do nome de propósito: o Select guarda o texto
            # da opção, e assim ele ordena na sequência dos meses em vez de
            # ordenar em ordem alfabética (Abril, Agosto, Dezembro...).
            "fieldname": "mes_de_emissao_nf",
            "fieldtype": "Select",
            "label": "Mês de Emissão NF",
            "options": (
                "\n01 - Janeiro\n02 - Fevereiro\n03 - Março\n04 - Abril"
                "\n05 - Maio\n06 - Junho\n07 - Julho\n08 - Agosto"
                "\n09 - Setembro\n10 - Outubro\n11 - Novembro\n12 - Dezembro"
            ),
            "read_only": 1,
            "insert_after": "data_de_emissao_nf",
        },
        {
            # Texto, e não Int, porque um Int vazio no Frappe vale 0 — e o
            # campo mostraria "0" na tela quando a data fosse apagada, já que
            # a regra que esconde campo somente-leitura vazio não trata 0 como
            # vazio. Como ano tem sempre 4 dígitos, ordenar como texto dá o
            # mesmo resultado que ordenar como número.
            "fieldname": "ano_de_emissao_nf",
            "fieldtype": "Data",
            "label": "Ano de Emissão NF",
            "read_only": 1,
            "insert_after": "mes_de_emissao_nf",
        },
        # Mês e ano da meta de faturamento, abaixo da Data de Vencimento.
        #
        # Saem da mesma Data de Emissão NF, mas com regra oposta à dos campos
        # acima: aqui o valor é sugestão, não espelho. Só é preenchido quando
        # está vazio, e continua editável depois do envio da fatura — é assim
        # que uma nota emitida no fim do mês pode ser contada na meta do mês
        # seguinte.
        {
            "fieldname": "mes_da_meta",
            "fieldtype": "Select",
            "label": "Mês da Meta",
            "options": (
                "\n01 - Janeiro\n02 - Fevereiro\n03 - Março\n04 - Abril"
                "\n05 - Maio\n06 - Junho\n07 - Julho\n08 - Agosto"
                "\n09 - Setembro\n10 - Outubro\n11 - Novembro\n12 - Dezembro"
            ),
            "allow_on_submit": 1,
            "insert_after": "due_date",
        },
        {
            "fieldname": "ano_da_meta",
            "fieldtype": "Data",
            "label": "Ano da Meta",
            "allow_on_submit": 1,
            "insert_after": "mes_da_meta",
        },
    ],
    "Supplier": [
        {
            "fieldname": "custom_homologacao",
            "fieldtype": "Select",
            "label": "Homologação",
            "options": "Sim\nNão\nNA/Dispensado",
            "insert_after": "is_transporter",
        },
    ],
    "Employee": [
        {
            "fieldname": "custom_escolaridade",
            "fieldtype": "Select",
            "label": "Escolaridade",
            "options": (
                "\nEnsino fundamental incompleto\nEnsino fundamental completo"
                "\nEnsino médio incompleto\nEnsino médio completo"
                "\nEnsino superior incompleto\nEnsino superior completo"
            ),
            "insert_after": "date_of_birth",
        },
    ],
}


def setup_custom_fields():
    create_custom_fields(CUSTOM_FIELDS, update=True)
