import frappe
from datetime import datetime, timedelta

def execute(filters=None):
    from_date = None
    to_date = None
    if filters:
        if filters.get("from_date"):
            from_date = datetime.strptime(filters.get("from_date"), "%Y-%m-%d")
        if filters.get("to_date"):
            to_date = datetime.strptime(filters.get("to_date"), "%Y-%m-%d") + timedelta(days=1) - timedelta(seconds=1)

    columns = [
        {"label": "Nome", "fieldname": "name", "fieldtype": "Link", "options": "Ordem Servico Externa", "width": 350},
        {"label": "Cliente", "fieldname": "customer", "fieldtype": "Data", "width": 200},
        {"label": "Status", "fieldname": "status_order_service", "fieldtype": "Data", "width": 200},
        {"label": "Finalizado Em", "fieldname": "end_repair_time", "fieldtype": "Date", "width": 200},
    ]

    docs = frappe.get_all(
        "Ordem Servico Externa",
        filters={"status_order_service": "Encerrada"},
        fields=["name", "customer", "status_order_service", "end_repair_time"]
    )

    data = []
    for doc in docs:
        if not doc.end_repair_time:
            continue  # Ignora OS sem data

        try:
            dt = datetime.strptime(doc.end_repair_time, "%d-%m-%Y %H:%M:%S")
        except Exception:
            try:
                dt = datetime.strptime(doc.end_repair_time, "%d-%m-%Y")
            except:
                continue  # Ignora se falhar o parse

        if from_date and dt < from_date:
            continue
        if to_date and dt > to_date:
            continue

        doc.end_repair_time = dt.strftime("%Y-%m-%d")
        data.append(doc)

    # Adiciona linha total
    data.append({
        "name": f"Total: {len(data)} equipamentos realizados nesse período",
        "customer": "",
        "status_order_service": "",
        "end_repair_time": ""
    })

    return columns, data
