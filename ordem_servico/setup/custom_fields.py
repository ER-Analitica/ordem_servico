from __future__ import unicode_literals

import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter
from frappe.model.rename_doc import rename_doc

# Segmento de mercado — a mesma lista para Cliente, Lead e Oportunidade.
#
# As três divergiam: o Cliente tinha 15 opções (com "Distribuidor" e "Autarquia
# Federal", acrescentadas em 2026 e nunca replicadas), o Lead e a Oportunidade
# tinham 13, e a acentuação estava errada em graus diferentes nos três.
#
# Unificar importa por causa do `fetch_from` da Oportunidade, que puxa o
# segmento do cliente: com listas diferentes, um cliente marcado como
# "Distribuidor" gerava valor inválido na Oportunidade e travava o save.
SEGMENTOS = (
    "Saneamento\nAlimentos\nBebidas\nLacticínios"
    "\nFarmacêuticos\nAcadêmico\nPetroquímico\nQuímico"
    "\nAçúcar e Álcool\nPapel e Celulose\nPrestadores de Serviços"
    "\nLaboratórios de Análises\nIndústria de Transformação"
    "\nDistribuidor\nAutarquia Federal"
)

# No Cliente o campo é obrigatório e a lista não tem opção vazia; nos outros
# dois ela existe, e é o que permite deixar o segmento em branco.
SEGMENTOS_COM_VAZIO = "\n" + SEGMENTOS


def _campo_segmento(opcoes):
    """Só a lista de opções é tocada.

    O `create_custom_fields` atualiza apenas as chaves informadas, então
    `insert_after` e as demais propriedades dos campos, que existem desde 2018,
    permanecem como estão.
    """
    return {
        "fieldname": "segmento",
        "fieldtype": "Select",
        "label": "Segmento",
        "options": opcoes,
    }


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
    "Quotation": [
        {
            # Campo já existente: ganha o "Buscar De" apontando para o cliente.
            # Com `fetch_if_empty`, o Frappe preenche quando está vazio e nunca
            # mais mexe — a edição feita no orçamento é respeitada.
            "fieldname": "prazo_de_pagamento",
            "fieldtype": "Data",
            "label": "Prazo de pagamento",
            "insert_after": "tc_name",
            "fetch_from": "party_name.prazo_de_pagamento",
            "fetch_if_empty": 1,
        },
    ],
    "Customer": [
        # Condições e prazo padrão do cliente, logo abaixo dos detalhes dos
        # termos — que já seguem o mesmo caminho para o orçamento.
        #
        # Mesmos fieldnames do Quotation de propósito: é o padrão que o
        # `detalhes_dos_termos_e_condicoes` já usa, e deixa a cópia simétrica.
        # Aqui valem como sugestão; quem monta o orçamento pode divergir sem
        # que isso volte para o cadastro.
        {
            "fieldname": "tc_name",
            "fieldtype": "Link",
            "label": "Condições",
            "options": "Terms and Conditions",
            "insert_after": "detalhes_dos_termos_e_condicoes",
        },
        {
            "fieldname": "prazo_de_pagamento",
            "fieldtype": "Data",
            "label": "Prazo de pagamento",
            "insert_after": "tc_name",
        },
        _campo_segmento(SEGMENTOS),
    ],
    "Lead": [
        _campo_segmento(SEGMENTOS_COM_VAZIO),
    ],

    "Opportunity": [
        _campo_segmento(SEGMENTOS_COM_VAZIO),
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


# Propriedades de campos nativos, que não são Custom Field e por isso não
# entram no dicionário acima. Cada item é (doctype, campo, propriedade, valor,
# tipo).
PROPERTY_SETTERS = (
    # O "Condições" do Orçamento é o `tc_name` nativo do ERPNext. Aqui ele
    # ganha o "Buscar De" do cliente, com a mesma regra do prazo: preenche
    # quando está vazio e respeita o que for digitado depois.
    ("Quotation", "tc_name", "fetch_from", "party_name.tc_name", "Small Text"),
    ("Quotation", "tc_name", "fetch_if_empty", "1", "Check"),
    # O Cliente e a Oportunidade têm Property Setter para as opções do Segmento,
    # e ele vence o Custom Field na hora de montar o formulário. Sem atualizar
    # os dois aqui, a correção do Custom Field acima não aparece na tela.
    ("Customer", "segmento", "options", SEGMENTOS, "Text"),
    ("Opportunity", "segmento", "options", SEGMENTOS_COM_VAZIO, "Text"),
)


def setup_custom_fields():
    # O bloco do Cliente sai separado por causa de uma inconsistência que já
    # existe naquele doctype: o campo Tax ID está oculto e obrigatório ao mesmo
    # tempo, sem valor padrão. O Frappe revalida o doctype inteiro sempre que
    # um campo personalizado é adicionado, e recusa a operação por causa disso.
    #
    # O Tax ID vem de uma integração antiga e não deve ser mexido, então aqui
    # pulamos apenas essa revalidação — os campos continuam sendo criados e a
    # coluna, gerada normalmente. O que se perde é a checagem automática de
    # conflito de nome, conferida à mão: nem `tc_name` nem `prazo_de_pagamento`
    # existiam no Cliente.
    campos_cliente = {"Customer": CUSTOM_FIELDS["Customer"]}
    demais = {dt: campos for dt, campos in CUSTOM_FIELDS.items() if dt != "Customer"}

    create_custom_fields(demais, update=True)
    create_custom_fields(campos_cliente, update=True, ignore_validate=True)

    for doctype, campo, propriedade, valor, tipo in PROPERTY_SETTERS:
        _aplicar_property_setter(doctype, campo, propriedade, valor, tipo)


def _aplicar_property_setter(doctype, campo, propriedade, valor, tipo):
    """Cria ou atualiza um Property Setter, sem quebrar em execução repetida.

    A busca é pela identidade real — doctype, campo e propriedade — e não pelo
    nome do registro. Existem Property Setters no sistema cujo nome não bate
    com o próprio `doc_type`: o Frappe monta o nome na criação e não renomeia
    quando alguém troca o doctype depois, pela tela.

    Quando o nome que o Frappe vai gerar está ocupado por um desses registros
    desalinhados, devolvemos a ele o nome que corresponde ao seu próprio
    doc_type. Nada é apagado e nenhum valor é alterado — só o nome volta a
    bater com o conteúdo, que é a regra do próprio Frappe.

    A revalidação do doctype fica desligada pelo mesmo motivo do bloco do
    Cliente: uma inconsistência preexistente em qualquer campo derrubaria a
    operação inteira, mesmo sem relação com o que está sendo alterado.
    """
    existente = frappe.db.sql(
        "SELECT name, value FROM `tabProperty Setter` "
        "WHERE doc_type = %s AND field_name = %s AND property = %s",
        (doctype, campo, propriedade),
        as_dict=True,
    )

    if existente:
        if existente[0].value != valor:
            frappe.db.set_value("Property Setter", existente[0].name, "value", valor)
            frappe.clear_cache(doctype=doctype)
        return

    nome = "{}-{}-{}".format(doctype, campo, propriedade)
    ocupante = frappe.db.sql(
        "SELECT doc_type, field_name, property FROM `tabProperty Setter` WHERE name = %s",
        nome,
        as_dict=True,
    )

    if ocupante:
        dono = ocupante[0]
        nome_correto = "{}-{}-{}".format(dono.doc_type, dono.field_name, dono.property)
        if nome_correto != nome:
            rename_doc(
                "Property Setter",
                nome,
                nome_correto,
                force=True,
                ignore_permissions=True,
                show_alert=False,
            )

    make_property_setter(
        doctype,
        campo,
        propriedade,
        valor,
        tipo,
        for_doctype=False,
        validate_fields_for_doctype=False,
    )
