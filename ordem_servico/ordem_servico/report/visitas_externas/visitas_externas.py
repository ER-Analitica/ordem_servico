import frappe
from frappe.utils import getdate

def execute(filters=None):
    ano = filters.get("ano") if filters else getdate(frappe.utils.nowdate()).year

    columns = [
        {"label": "Mês", "fieldname": "mes_label", "fieldtype": "Data", "width": 150},
        {"label": "Visitas Externas", "fieldname": "Visitas Externas", "fieldtype": "Int", "width": 150},
        #{"label": "Consertos Internos", "fieldname": "Consertos Internos", "fieldtype": "Int", "width": 150},
    ]

    MESES = {
        1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
    }

    # Visitas Externas
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

    visitas_externas_mes = {r["numero_mes"]: r["qtd"] for r in visitas_externas}


    data = []
    for mes in range(1, 13):
        mes_nome = MESES.get(mes, str(mes))
        mes_label = f"{mes_nome}/{ano}"
        data.append({
            "mes_label": mes_label,
            "Visitas Externas": visitas_externas_mes.get(mes, 0),
        })

    return columns, data
