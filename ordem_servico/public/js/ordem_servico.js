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
	refresh(frm) {
		travar_campos_equipamento_os(frm);

		if (frm.fields_dict.informe_numero_serie) {
			frm.set_df_property(
				"informe_numero_serie",
				"description",
				"Digite o número de série e confira se o equipamento já possui cadastro antes de criar um novo. " +
				"Os dados do equipamento só podem ser alterados pelo botão \"Atualizar Equipamento\"."
			);
		}

		if (frm.doc.informe_numero_serie) {
			frm.add_custom_button('Atualizar Equipamento', () => {
				abrir_atualizacao_equipamento(frm);
			});
		}
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

// --- Equipamento na OS: campos travados + atualização via popup ---
// Os dados de equipamento na OS vêm somente do cadastro (Equipamentos).
// Alterações passam pelo popup, que grava direto no cadastro e roda a
// validação de duplicidade no servidor.

function travar_campos_equipamento_os(frm) {
	var campos = [
		"serie_number", "equipment_description", "equipment_model",
		"marca_equipamento", "equipment_tag", "tipo_equipamento",
		"capacidade_equipamento"
	];
	campos.forEach(function (campo) {
		if (frm.fields_dict[campo]) {
			frm.set_df_property(campo, "read_only", 1);
		}
	});
}

function abrir_atualizacao_equipamento(frm) {
	var equipamento = frm.doc.informe_numero_serie;
	if (!equipamento) return;

	frappe.db.get_doc("Equipamentos", equipamento).then(function (eq) {
		var d = new frappe.ui.Dialog({
			title: "Atualizar Equipamento " + equipamento,
			fields: [
				{ fieldname: "numero_serie", fieldtype: "Data", label: "Número de Série", default: eq.numero_serie, reqd: 1 },
				{ fieldname: "descricao", fieldtype: "Link", options: "Nome Equipamento", label: "Equipamento", default: eq.descricao, reqd: 1 },
				{ fieldname: "modelo_equipamento", fieldtype: "Link", options: "Modelo do Equipamento", label: "Modelo", default: eq.modelo_equipamento, reqd: 1 },
				{ fieldname: "marca_equipamento", fieldtype: "Link", options: "Marca do Equipamento", label: "Marca", default: eq.marca_equipamento, reqd: 1 },
				{ fieldname: "tipo_equipamento", fieldtype: "Link", options: "Tipo do Equipamento", label: "Tipo", default: eq.tipo_equipamento },
				{ fieldname: "tag", fieldtype: "Data", label: "Tag", default: eq.tag },
				{ fieldname: "capacidade", fieldtype: "Data", label: "Capacidade", default: eq.capacidade }
			],
			primary_action_label: "Atualizar",
			primary_action: function (values) {
				frappe.call({
					method: "ordem_servico.doc_events.validacao_duplicidade_equipamentos.atualizar_equipamento",
					args: { name: equipamento, valores: values },
					callback: function (r) {
						d.hide();
						var novo = r.message || values;
						// Reflete os novos dados nos campos da OS
						frm.set_value("serie_number", novo.numero_serie);
						frm.set_value("equipment_description", novo.descricao);
						frm.set_value("equipment_model", novo.modelo_equipamento);
						frm.set_value("marca_equipamento", novo.marca_equipamento);
						frm.set_value("equipment_tag", novo.tag);
						frm.set_value("tipo_equipamento", novo.tipo_equipamento);
						frm.set_value("capacidade_equipamento", novo.capacidade);
						frappe.show_alert("Equipamento atualizado. Salve a OS para gravar.");
					}
				});
			}
		});
		d.show();
	});
}
