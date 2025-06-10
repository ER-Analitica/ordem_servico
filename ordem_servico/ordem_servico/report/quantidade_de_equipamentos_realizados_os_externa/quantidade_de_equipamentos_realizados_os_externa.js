frappe.query_reports["Quantidade de equipamentos realizados OS Externa"] = {
    "filters": [
        {
            "fieldname": "from_date",
            "label": __("Data Inicial"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1), // opcional: padrão 1 mês atrás
            "reqd": 0
        },
        {
            "fieldname": "to_date",
            "label": __("Data Final"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(), // padrão hoje
            "reqd": 0
        }
    ]
};
