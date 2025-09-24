import frappe
from frappe.utils import getdate

def execute(filters=None):
    ano = filters.get("ano") if filters else getdate(frappe.utils.nowdate()).year

    columns = [
        {"label": "Mês", "fieldname": "mes_label", "fieldtype": "Data", "width": 150},
        {"label": "Orcamentos Internos", "fieldname": "Orcamentos Internos", "fieldtype": "Int", "width": 120},
        {"label": "Consertos Internos", "fieldname": "Consertos Internos", "fieldtype": "Int", "width": 150},
        {"label": "Equipamentos Internos", "fieldname": "Equipamentos Internos", "fieldtype": "Int", "width": 150},
        {"label": "Visitas Externas", "fieldname": "Visitas Externas", "fieldtype": "Int", "width": 150},
        {"label": "Equipamentos Externos", "fieldname":"Equipamentos Externos", "fieldtype":"Int", "width":150},
        {"label": "Equipamentos em Garantia", "fieldname":"Equipamentos em Garantia", "fieldtype":"Int", "width":150}
    ]

    MESES = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    # Consulta Quotation (sem mudanças)
    quotation_resultados = frappe.db.sql(f"""
        SELECT 
            m.mes AS numero_mes,
            IFNULL(COUNT(q.name), 0) AS qtd
        FROM (
            SELECT 1 AS mes UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
        ) m
        LEFT JOIN `tabQuotation` q 
            ON MONTH(q.transaction_date) = m.mes 
            AND YEAR(q.transaction_date) = %(ano)s
            AND q.os_interna_link LIKE '%%OS%%'
            AND (q.amended_from IS NULL OR q.amended_from NOT LIKE '%%-%%')
        GROUP BY m.mes
        ORDER BY m.mes
    """, {"ano": ano}, as_dict=True)

    # Consulta Ordem Servico Interna (tratando a data com STR_TO_DATE)
    ordem_servico_resultados = frappe.db.sql(f"""
        SELECT 
            m.mes AS numero_mes,
            IFNULL(COUNT(o.name), 0) AS qtd
        FROM (
            SELECT 1 AS mes UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
        ) m
        LEFT JOIN `tabOrdem Servico Interna` o 
            ON MONTH(STR_TO_DATE(o.end_repair_time, '%%d-%%m-%%Y %%H:%%i:%%s')) = m.mes
            AND YEAR(STR_TO_DATE(o.end_repair_time, '%%d-%%m-%%Y %%H:%%i:%%s')) = %(ano)s
            AND o.status_order_service IN ('Aguardando Retirada', 'Embalar', 'Encerrada', 'Sem Conserto')
        GROUP BY m.mes
        ORDER BY m.mes
    """, {"ano": ano}, as_dict=True)


    equipamentos_interno_resultados = frappe.db.sql(f"""
        SELECT 
            m.mes AS numero_mes,
            IFNULL(COUNT(o.name), 0) AS qtd
        FROM (
            SELECT 1 AS mes UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
        ) m
        LEFT JOIN `tabOrdem Servico Interna` o 
            ON MONTH(o.entry_date) = m.mes 
            AND YEAR(o.entry_date) = %(ano)s
        GROUP BY m.mes
        ORDER BY m.mes
    """, {"ano": ano}, as_dict=True)

    visitas_externas = frappe.db.sql(f"""
        SELECT 
            m.mes AS numero_mes,
            IFNULL(COUNT(q.name), 0) AS qtd
        FROM (
            SELECT 1 AS mes UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
        ) m
        LEFT JOIN `tabCriador de Ordens de Servico em Lote` q 
            ON MONTH(q.data_do_servico) = m.mes 
            AND YEAR(q.data_do_servico) = %(ano)s
            AND q.ordem_servico = 'Ordem Servico Externa'
        GROUP BY m.mes
        ORDER BY m.mes
    """, {"ano": ano}, as_dict=True)

    equipamentos_externos_resultados = frappe.db.sql(f"""
        SELECT 
            m.mes AS numero_mes,
            IFNULL(COUNT(o.name), 0) AS qtd
        FROM (
            SELECT 1 AS mes UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
        ) m
        LEFT JOIN `tabOrdem Servico Externa` o 
            ON MONTH(STR_TO_DATE(o.end_repair_time, '%%d-%%m-%%Y %%H:%%i:%%s')) = m.mes
            AND YEAR(STR_TO_DATE(o.end_repair_time, '%%d-%%m-%%Y %%H:%%i:%%s')) = %(ano)s
            AND o.status_order_service = 'Encerrada'
        GROUP BY m.mes
        ORDER BY m.mes
    """, {"ano": ano}, as_dict=True)


    equipamentos_garantia = frappe.db.sql(f"""
         SELECT 
            m.mes AS numero_mes,
            IFNULL(COUNT(o.name), 0) AS qtd
        FROM (
            SELECT 1 AS mes UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL
            SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL
            SELECT 9 UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
        ) m
        LEFT JOIN `tabOrdem Servico Interna` o 
            ON MONTH(o.entry_date) = m.mes 
            AND YEAR(o.entry_date) = %(ano)s
            AND o.warranty = 1
        GROUP BY m.mes
        ORDER BY m.mes
    """, {"ano": ano}, as_dict=True)

    



    quotation_por_mes = {r["numero_mes"]: r["qtd"] for r in quotation_resultados}
    os_por_mes = {r["numero_mes"]: r["qtd"] for r in ordem_servico_resultados}
    equipamentos_internos_por_mes = {r["numero_mes"]: r["qtd"] for r in equipamentos_interno_resultados}
    visitas_externas_mes = {r["numero_mes"]: r["qtd"] for r in visitas_externas}
    equipamentos_externos_por_mes = {r["numero_mes"]: r["qtd"] for r in equipamentos_externos_resultados}
    equipamentos_garantia_por_mes = {r["numero_mes"]: r["qtd"] for r in equipamentos_garantia}

    data = []
    for mes in range(1, 13):
        mes_nome = MESES.get(mes, str(mes))
        mes_label = f"{mes_nome}/{ano}"
        data.append({
            "mes_label": mes_label,
            "Orcamentos Internos": quotation_por_mes.get(mes, 0),
            "Consertos Internos": os_por_mes.get(mes, 0),
            "Equipamentos Internos": equipamentos_internos_por_mes.get(mes, 0),
            "Visitas Externas": visitas_externas_mes.get(mes, 0),
            "Equipamentos Externos": equipamentos_externos_por_mes.get(mes, 0),
            "Equipamentos em Garantia": equipamentos_garantia_por_mes.get(mes, 0)
        })

    return columns, data
