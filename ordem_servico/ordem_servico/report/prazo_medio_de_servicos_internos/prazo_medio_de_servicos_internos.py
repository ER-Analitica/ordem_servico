import frappe

def execute(filters=None):
    if not filters:
        filters = {}

    start_date = filters.get("start_date")
    end_date = filters.get("end_date")

    conditions = []
    params = {}

    # Filtro por período de entrada
    if start_date and end_date:
        conditions.append("o.entry_date BETWEEN %(start_date)s AND %(end_date)s")
        params["start_date"] = start_date
        params["end_date"] = end_date

    # Ignora OS sem data de orçamento
    conditions.append("o.quotation_date IS NOT NULL AND o.quotation_date != ''")

    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

    # Calcula a média de diferença em dias
    data = frappe.db.sql(f"""
        SELECT
            ROUND(AVG(DATEDIFF(o.quotation_date, o.entry_date)), 2) AS media_dias
        FROM `tabOrdem Servico Interna` o
        {where_clause}
    """, params, as_dict=True)

    media_dias = data[0].media_dias if data and data[0].media_dias is not None else 0

    # Retorna apenas uma linha (para o gráfico mostrar uma barra)
    result = [{
        "descricao": "Prazo Médio de Orçamentos",
        "media_dias": media_dias
    }]

    columns = [
        {"label": "Descrição", "fieldname": "descricao", "fieldtype": "Data", "width": 200},
        {"label": "Média (dias)", "fieldname": "media_dias", "fieldtype": "Float", "width": 150}
    ]

    return columns, result
