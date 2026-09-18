// Copyright (c) 2026, laugusto and contributors
// For license information, please see license.txt

const SITUACOES_DO_PEDIDO = [
	"Em Espera",
	"A Receber e Faturar",
	"A Faturar",
	"A Receber",
	"Entregue",
	"Concluído",
	"Fechado",
	"Cancelado",
];

frappe.query_reports["Acompanhamento de Compras"] = {
	filters: [
		{
			fieldname: "company",
			label: "Empresa",
			fieldtype: "Link",
			options: "Company",
			default: frappe.defaults.get_user_default("Company"),
		},
		{
			fieldname: "cost_center",
			label: "Centro de Custo",
			fieldtype: "Link",
			options: "Cost Center",
		},
		{
			fieldname: "project",
			label: "Projeto",
			fieldtype: "Link",
			options: "Project",
		},
		{
			fieldname: "from_date",
			label: "Data Inicial",
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[1],
		},
		{
			fieldname: "to_date",
			label: "Data Final",
			fieldtype: "Date",
			default: erpnext.utils.get_fiscal_year(frappe.datetime.get_today(), true)[2],
		},
		{
			fieldname: "situacao",
			label: "Situação do Pedido",
			fieldtype: "MultiSelectList",
			// Em branco: esconde Fechado, Concluído e Cancelado, como no relatório padrão.
			get_data: function (txt) {
				return SITUACOES_DO_PEDIDO.filter((situacao) =>
					situacao.toLowerCase().includes((txt || "").toLowerCase())
				).map((situacao) => ({ value: situacao, description: "" }));
			},
		},
	],
};
