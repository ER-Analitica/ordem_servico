frappe.query_reports["Prazo Medio de Servicos Internos"] = {
    "filters": [
        {
            fieldname: "start_date",
            label: __("Data Inicial"),
            fieldtype: "Date",
            default: frappe.datetime.month_start(),
            reqd: 0
        },
        {
            fieldname: "end_date",
            label: __("Data Final"),
            fieldtype: "Date",
            default: frappe.datetime.month_end(),
            reqd: 0
        }
    ]
};
