// Copyright (c) 2018, laugusto and contributors
// For license information, please see license.txt

frappe.ui.form.on(cur_frm.doctype, {
	onload() {
		cur_frm.fields_dict.informe_numero_serie.get_query = () => {
			return {
				filters: {
					'customer': cur_frm.doc.customer
				}
			}
		}
		cur_frm.fields_dict.contact_link.get_query = () => {
			return {
				filters: {
					'link_doctype': 'Customer', // ou 'Company', dependendo do vínculo
					'link_name': cur_frm.doc.customer // ou cur_frm.doc.company
				}
			}
		}
		
		cur_frm.fields_dict.initial_scheduled_to.get_query = () => {
			return {
				filters: {
					'role_profile_name': ['in', ['Diretor Executivo', 'Supervisor Técnico', 'Assistente Técnico em Eletrônica', 'Estágiário Técnico', 'Gerente Técnico', 'Coordenador Técnico', 'Técnico em Eletrônica Senior', 'Técnico em Eletrônica Pleno', 'Técnico em Eletrônica Junior', 'Diretor Técnico']],
					'enabled': '1'
				}
			}
		}
		cur_frm.fields_dict.final_scheduled_to.get_query = () => {
			return {
				filters: {
					'role_profile_name': ['in', ['Diretor Executivo', 'Supervisor Técnico', 'Assistente Técnico em Eletrônica', 'Estágiário Técnico', 'Gerente Técnico', 'Coordenador Técnico', 'Técnico em Eletrônica Senior', 'Técnico em Eletrônica Pleno', 'Técnico em Eletrônica Junior', 'Diretor Técnico']],
					'enabled': '1'
				}
			}
		}
		cur_frm.fields_dict.os_items.grid.get_field("item_code").get_query = function(doc, cdt, cdn) {
			var child = locals[cdt][cdn];
			return {
				query: "erpnext.controllers.queries.item_query"
			};
		};
		

		
		
		
		/*cur_frm.fields_dict.initial_scheduled_by.get_query = () => {
			return {
				filters: {
					'department': ['in', ['Diretoria - ER', 'Vendas - ER', 'Comercial - ER']],
					'status': 'Active'
				}
			}
		}*/
		/*cur_frm.fields_dict.technical_person.get_query = () => {
			return {
				filters: {
					'department': ['in', ['Diretoria - ER', 'Assistência Técnica - ER']],
					'status': 'Active'
				}
			}
		}*/
	
		/*cur_frm.fields_dict.final_scheduled_by.get_query = () => {
			return {
				filters: {
					'department': ['in', ['Diretoria - ER', 'Vendas - ER', 'Comercial - ER']],
					'status': 'Active'
				}
			}
		}*/
		/*cur_frm.fields_dict.repaired_by.get_query = () => {
			return {
				filters: {
					'department': ['in', ['Diretoria - ER', 'Assistência Técnica - ER']],
					'status': 'Active'
				}
			}
		}*/
	},
	/*
	serie_number(frm) {
		const { serie_number } = frm.doc
		if (serie_number) {
			const { equipment_model } = frm.doc
			frappe.call({
				method: 'ordem_servico.ordem_servico.utils.get_repair_and_quotation_times',
				args: {
					equipment: equipment_model
				},
				callback(r) {
					const data = r.message
					frm.doc.quotation_time = data.quotation_time
					frm.doc.repair_time = data.repair_time
					frm.refresh_field('quotation_time')
					frm.refresh_field('repair_time')
				}
			})
		}
	},*/
	customer: function(frm) {
        // Limpa o valor do campo serie_number quando o campo customer é alterado
        frm.set_value('informe_numero_serie', '');
	},
	start_repair(frm) {
		const { __unsaved } = cur_frm.doc
		if (__unsaved) {
			frappe.throw('Favor salvar documento!')
		}
		frappe.call({
			method: 'ordem_servico.ordem_servico.utils.get_time_now',
			args: {
				doctype: frm.doc.doctype,
				docname: frm.doc.name,
				trigger: 'start_repair'
			}
		})
		frm.reload_doc()
		show_alert('Conserto iniciado.')
	},
	/*end_repair(frm) {
		const { __unsaved, quotation_status } = cur_frm.doc
		if (__unsaved) {
			frappe.throw('Favor salvar documento!')
		}  
		else if (!quotation_status) {
			frappe.throw('Favor colocar Status do Orçamento!')
		}
		else {
			const { doctype, name } = frm.doc
			frappe.call({
				method: 'ordem_servico.ordem_servico.utils.get_time_now',
				args: {
					doctype: doctype,
					docname: name,
					trigger: 'end_repair'
				}
			})
		}
		frm.reload_doc()
		show_alert('Conserto finalizado.')
	}*/
})
