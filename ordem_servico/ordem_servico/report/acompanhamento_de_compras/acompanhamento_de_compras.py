# Copyright (c) 2026, laugusto and contributors
# For license information, please see license.txt

# Baseado no relatorio padrao "Procurement Tracker" da ERPNext, com um filtro
# de situacao do pedido de compra. Sem o filtro, as situacoes Fechado,
# Concluido e Cancelado ficam de fora, como no relatorio original.

import json

import frappe
from frappe.utils import flt

SITUACOES_OCULTAS = ("Closed", "Completed", "Cancelled")

# O filtro mostra a situacao em portugues; o banco guarda em ingles.
SITUACOES = {
    "Em Espera": "On Hold",
    "A Receber e Faturar": "To Receive and Bill",
    "A Faturar": "To Bill",
    "A Receber": "To Receive",
    "Entregue": "Delivered",
    "Concluído": "Completed",
    "Fechado": "Closed",
    "Cancelado": "Cancelled",
}

# Para exibir a coluna Situação em portugues, tanto do pedido quanto da
# solicitacao de material.
SITUACOES_EM_PORTUGUES = {ingles: portugues for portugues, ingles in SITUACOES.items()}
SITUACOES_EM_PORTUGUES.update(
    {
        "Draft": "Rascunho",
        "Submitted": "Enviado",
        "Stopped": "Interrompido",
        "Pending": "Pendente",
        "Partially Ordered": "Parcialmente Pedido",
        "Partially Received": "Parcialmente Recebido",
        "Ordered": "Pedido",
        "Issued": "Emitido",
        "Transferred": "Transferido",
        "Received": "Recebido",
    }
)


def execute(filters=None):
    columns = get_columns(filters)
    data = get_data(filters)
    return columns, data


def get_columns(filters):
    return [
        {
            "label": "Data da Solicitação",
            "fieldname": "material_request_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": "Solicitação de Material",
            "options": "Material Request",
            "fieldname": "material_request_no",
            "fieldtype": "Link",
            "width": 160,
        },
        {
            "label": "Centro de Custo",
            "options": "Cost Center",
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": "Projeto",
            "options": "Project",
            "fieldname": "project",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": "Local Solicitante",
            "options": "Warehouse",
            "fieldname": "requesting_site",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": "Solicitante",
            "options": "User",
            "fieldname": "requestor",
            "fieldtype": "Link",
            "width": 140,
        },
        {
            "label": "Item",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 150,
        },
        {"label": "Quantidade", "fieldname": "quantity", "fieldtype": "Float", "width": 110},
        {
            "label": "Unidade",
            "options": "UOM",
            "fieldname": "unit_of_measurement",
            "fieldtype": "Link",
            "width": 100,
        },
        {"label": "Situação", "fieldname": "status", "fieldtype": "Data", "width": 160},
        {
            "label": "Data do Pedido",
            "fieldname": "purchase_order_date",
            "fieldtype": "Date",
            "width": 130,
        },
        {
            "label": "Pedido de Compra",
            "options": "Purchase Order",
            "fieldname": "purchase_order",
            "fieldtype": "Link",
            "width": 160,
        },
        {
            "label": "Fornecedor",
            "options": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Link",
            "width": 160,
        },
        {
            "label": "Custo Estimado",
            "fieldname": "estimated_cost",
            "fieldtype": "Float",
            "width": 130,
        },
        {"label": "Custo Real", "fieldname": "actual_cost", "fieldtype": "Float", "width": 130},
        {
            "label": "Valor do Pedido",
            "fieldname": "purchase_order_amt",
            "fieldtype": "Float",
            "width": 140,
        },
        {
            "label": "Valor do Pedido (Moeda da Empresa)",
            "fieldname": "purchase_order_amt_in_company_currency",
            "fieldtype": "Float",
            "width": 180,
        },
        {
            "label": "Entrega Prevista",
            "fieldname": "expected_delivery_date",
            "fieldtype": "Date",
            "width": 140,
        },
        {
            "label": "Entrega Real",
            "fieldname": "actual_delivery_date",
            "fieldtype": "Date",
            "width": 140,
        },
    ]


def get_situacoes(filters):
    """Situacoes escolhidas no filtro, ja limpas. Lista vazia = filtro nao usado."""
    situacoes = (filters or {}).get("situacao") or []

    if isinstance(situacoes, str):
        situacoes = situacoes.strip()
        if situacoes.startswith("["):
            situacoes = json.loads(situacoes)
        else:
            situacoes = [situacoes]

    return [SITUACOES.get(situacao, situacao) for situacao in situacoes if situacao]


def aplicar_situacao(query, parent, situacoes):
    if situacoes:
        return query.where(parent.status.isin(situacoes))

    return query.where(parent.status.notin(SITUACOES_OCULTAS))


def apply_filters_on_query(filters, parent, child, query):
    if filters.get("company"):
        query = query.where(parent.company == filters.get("company"))

    if filters.get("cost_center") or filters.get("project"):
        query = query.where(
            (child.cost_center == filters.get("cost_center")) | (child.project == filters.get("project"))
        )

    if filters.get("from_date"):
        query = query.where(parent.transaction_date >= filters.get("from_date"))

    if filters.get("to_date"):
        query = query.where(parent.transaction_date <= filters.get("to_date"))

    return query


def get_data(filters):
    purchase_order_entry = get_po_entries(filters)
    mr_records, procurement_record_against_mr = get_mapped_mr_details(filters)
    pr_records = get_mapped_pr_records()
    pi_records = get_mapped_pi_records()

    procurement_record = []
    if procurement_record_against_mr:
        procurement_record += procurement_record_against_mr

    for po in purchase_order_entry:
        # solicitacoes de material ligadas ao item do pedido de compra
        material_requests = mr_records.get(po.material_request_item, [{}])

        for mr_record in material_requests:
            procurement_detail = {
                "material_request_date": mr_record.get("transaction_date"),
                "cost_center": po.cost_center,
                "project": po.project,
                "requesting_site": po.warehouse,
                "requestor": po.owner,
                "material_request_no": po.material_request,
                "item_code": po.item_code,
                "quantity": flt(po.qty),
                "unit_of_measurement": po.stock_uom,
                "status": SITUACOES_EM_PORTUGUES.get(po.status, po.status),
                "purchase_order_date": po.transaction_date,
                "purchase_order": po.parent,
                "supplier": po.supplier,
                "estimated_cost": flt(mr_record.get("amount")),
                "actual_cost": flt(pi_records.get(po.name)) or flt(po.amount),
                "purchase_order_amt": flt(po.amount),
                "purchase_order_amt_in_company_currency": flt(po.base_amount),
                "expected_delivery_date": po.schedule_date,
                "actual_delivery_date": pr_records.get(po.name),
            }
            procurement_record.append(procurement_detail)

    return procurement_record


def get_po_entries(filters):
    parent = frappe.qb.DocType("Purchase Order")
    child = frappe.qb.DocType("Purchase Order Item")

    query = (
        frappe.qb.from_(parent)
        .from_(child)
        .select(
            child.name,
            child.parent,
            child.cost_center,
            child.project,
            child.warehouse,
            child.material_request,
            child.material_request_item,
            child.item_code,
            child.stock_uom,
            child.qty,
            child.amount,
            child.base_amount,
            child.schedule_date,
            parent.transaction_date,
            parent.supplier,
            parent.status,
            parent.owner,
        )
        .where((parent.docstatus == 1) & (parent.name == child.parent))
        .groupby(parent.name, child.material_request_item)
    )
    query = aplicar_situacao(query, parent, get_situacoes(filters))
    query = apply_filters_on_query(filters, parent, child, query)

    return query.run(as_dict=True)


def get_mapped_mr_details(filters):
    mr_records = {}
    parent = frappe.qb.DocType("Material Request")
    child = frappe.qb.DocType("Material Request Item")

    query = (
        frappe.qb.from_(parent)
        .from_(child)
        .select(
            parent.transaction_date,
            parent.per_ordered,
            parent.owner,
            child.name,
            child.parent,
            child.amount,
            child.qty,
            child.item_code,
            child.uom,
            parent.status,
            child.project,
            child.cost_center,
        )
        .where((parent.per_ordered >= 0) & (parent.name == child.parent) & (parent.docstatus == 1))
    )
    query = apply_filters_on_query(filters, parent, child, query)

    mr_details = query.run(as_dict=True)

    procurement_record_against_mr = []
    for record in mr_details:
        if record.per_ordered:
            mr_records.setdefault(record.name, []).append(frappe._dict(record))
        else:
            procurement_record_details = dict(
                material_request_date=record.transaction_date,
                material_request_no=record.parent,
                requestor=record.owner,
                item_code=record.item_code,
                estimated_cost=flt(record.amount),
                quantity=flt(record.qty),
                unit_of_measurement=record.uom,
                status=SITUACOES_EM_PORTUGUES.get(record.status, record.status),
                actual_cost=0,
                purchase_order_amt=0,
                purchase_order_amt_in_company_currency=0,
                project=record.project,
                cost_center=record.cost_center,
            )
            procurement_record_against_mr.append(procurement_record_details)
    return mr_records, procurement_record_against_mr


def get_mapped_pi_records():
    """Custo real por item do pedido, vindo da nota fiscal de compra.

    Sem filtro por situacao do pedido: quem decide quais pedidos aparecem e a
    consulta principal. Assim o custo real tambem aparece em pedidos fechados,
    concluidos ou cancelados.
    """
    pi_item = frappe.qb.DocType("Purchase Invoice Item")
    pi_records = (
        frappe.qb.from_(pi_item)
        .select(pi_item.po_detail, pi_item.base_amount)
        .where((pi_item.docstatus == 1) & (pi_item.po_detail.isnotnull()))
    ).run()

    return frappe._dict(pi_records)


def get_mapped_pr_records():
    """Data de entrega real por item do pedido, vinda do recebimento de compra."""
    pr = frappe.qb.DocType("Purchase Receipt")
    pr_item = frappe.qb.DocType("Purchase Receipt Item")
    pr_records = (
        frappe.qb.from_(pr)
        .from_(pr_item)
        .select(pr_item.purchase_order_item, pr.posting_date)
        .where(
            (pr.docstatus == 1)
            & (pr.name == pr_item.parent)
            & (pr_item.purchase_order_item.isnotnull())
        )
    ).run()

    return frappe._dict(pr_records)
