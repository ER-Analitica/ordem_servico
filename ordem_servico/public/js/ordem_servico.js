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
		ocultar_campos_ipem(frm);

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

		if (frm.doc.anexo_certificado) {
			frm.add_custom_button('Revincular padrões', () => {
				revincular_padroes(frm);
			});
		}

		var pendentes = (frm.doc.rastreabilidade_padroes || []).filter(function (r) {
			return r.status !== "Vinculado" && r.status !== "Validade não cobre a data";
		});
		if (pendentes.length) {
			frm.add_custom_button(`Cadastrar padrões pendentes (${pendentes.length})`, () => {
				cadastrar_padroes_pendentes(frm);
			});
		}
	},
	informe_numero_serie(frm) {
		espelhar_dados_equipamento(frm);
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
		var f = frm.fields_dict[campo];
		if (!f || !f.$wrapper) return;
		// Não usar read_only: campo somente-leitura VAZIO fica oculto no Frappe.
		// Desabilitar o input mantém o campo sempre visível (mesmo vazio),
		// porém bloqueado para digitação.
		frm.set_df_property(campo, "read_only", 0);
		f.$wrapper.find("input, textarea").prop("disabled", true);
	});
}

function ocultar_campos_ipem(frm) {
	["observacoes_ipem"].forEach(function (campo) {
		if (frm.fields_dict[campo]) {
			frm.set_df_property(campo, "hidden", 1);
		}
	});
}

function espelhar_dados_equipamento(frm) {
	// Traz TODOS os dados do cadastro, inclusive vazios — assim o técnico
	// percebe na hora quando falta informação no cadastro do equipamento.
	var equipamento = frm.doc.informe_numero_serie;
	if (!equipamento) return;

	frappe.db.get_doc("Equipamentos", equipamento).then(function (eq) {
		var mapa = {
			serie_number: eq.numero_serie,
			equipment_description: eq.descricao,
			tipo_equipamento: eq.tipo_equipamento,
			equipment_model: eq.modelo_equipamento,
			marca_equipamento: eq.marca_equipamento,
			equipment_tag: eq.tag,
			capacidade_equipamento: eq.capacidade,
			pontos_calibracao: eq.pontos_calibracao
		};
		Object.keys(mapa).forEach(function (campo) {
			if (frm.fields_dict[campo]) {
				frm.set_value(campo, mapa[campo] || "");
			}
		});
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
				{ fieldname: "grandeza", fieldtype: "Link", options: "Grandeza", label: "Grandeza", default: eq.grandeza, reqd: 1 },
				{ fieldname: "tipo_equipamento", fieldtype: "Link", options: "Tipo do Equipamento", label: "Tipo", default: eq.tipo_equipamento },
				{ fieldname: "tag", fieldtype: "Data", label: "Tag", default: eq.tag },
				{ fieldname: "capacidade", fieldtype: "Data", label: "Capacidade", default: eq.capacidade },
				{ fieldname: "pontos_calibracao", fieldtype: "Small Text", label: "Pontos de Calibração", default: eq.pontos_calibracao },
				{ fieldname: "criterios_aceitacao", fieldtype: "Small Text", label: "Critérios de Aceitação", default: eq.criterios_aceitacao }
			],
			primary_action_label: "Atualizar",
			primary_action: function (values) {
				frappe.call({
					method: "ordem_servico.doc_events.validacao_duplicidade_equipamentos.atualizar_equipamento",
					args: { name: equipamento, valores: values },
					callback: function (r) {
						d.hide();
						var novo = r.message || values;
						// Reflete os novos dados nos campos da OS (mesmo vazios)
						var mapa = {
							serie_number: novo.numero_serie,
							equipment_description: novo.descricao,
							equipment_model: novo.modelo_equipamento,
							marca_equipamento: novo.marca_equipamento,
							equipment_tag: novo.tag,
							tipo_equipamento: novo.tipo_equipamento,
							capacidade_equipamento: novo.capacidade,
							pontos_calibracao: novo.pontos_calibracao,
							grandeza: novo.grandeza
						};
						Object.keys(mapa).forEach(function (campo) {
							if (frm.fields_dict[campo]) {
								frm.set_value(campo, mapa[campo] || "");
							}
						});
						frappe.show_alert("Equipamento atualizado. Salve a OS para gravar.");
					}
				});
			}
		});
		d.show();
	});
}

function revincular_padroes(frm) {
	frappe.call({
		method: "ordem_servico.doc_events.rastreabilidade_padroes.extrair_rastreabilidade",
		args: { doctype: frm.doc.doctype, name: frm.doc.name },
		freeze: true,
		freeze_message: "Extraindo e revinculando padrões...",
		callback: function (r) {
			var res = r.message || {};
			if (!res.ok) {
				var motivos = {
					sem_certificado: "Nenhum certificado anexado nesta OS.",
					pdf_sem_texto: "O PDF do certificado não tem texto (parece escaneado). Reenvie a versão gerada do Excel."
				};
				frappe.msgprint({
					title: "Não foi possível extrair",
					indicator: "orange",
					message: motivos[res.motivo] || "Não foi possível processar o certificado."
				});
				return;
			}
			var cor = res.alerta ? "orange" : "green";
			var msg = `${res.padroes} padrão(ões) processado(s).`;
			if (res.suspeitas > 0) {
				msg += `<br>⚠️ ${res.suspeitas} linha(s) com cara de padrão mas sem código detectado.`;
			}

			var pendentes = res.pendentes || [];
			if (pendentes.length) {
				var lista = pendentes.map(function (p) {
					return `• <b>${p.codigo}</b> (validade ${frappe.datetime.str_to_user(p.validade) || '—'}) — ${p.status}`;
				}).join("<br>");
				msg += "<br><br>⚠️ <b>Padrões pendentes de cadastro:</b><br>" + lista +
					"<br><br>Use o botão <b>Cadastrar padrões pendentes</b> no topo da OS.";
			}

			frappe.msgprint({ title: "Rastreabilidade dos padrões", indicator: cor, message: msg });
			frm.reload_doc();
		}
	});
}

function cadastrar_padroes_pendentes(frm) {
	var pendentes = (frm.doc.rastreabilidade_padroes || []).filter(function (r) {
		return r.status !== "Vinculado" && r.status !== "Validade não cobre a data";
	});

	if (!pendentes.length) {
		frappe.msgprint("Nenhum padrão pendente de cadastro nesta OS.");
		return;
	}

	_abrir_cadastro_pendente(frm, pendentes, 0);
}

function _abrir_cadastro_pendente(frm, pendentes, indice) {
    if (indice >= pendentes.length) {
        frappe.show_alert({ message: "Padrões pendentes processados.", indicator: "green" });
        frm.reload_doc();
        return;
    }

    var p = pendentes[indice];
    var restantes = pendentes.length - indice;

    var d = new frappe.ui.Dialog({
        title: `Cadastrar padrão ${p.codigo} (${restantes} pendente(s))`,
        fields: [
            {
                fieldtype: "HTML",
                options: `<div style="margin-bottom:10px;color:#6c757d;">
                    Dados extraídos do certificado — confira e anexe o arquivo do padrão.
                    <br>Motivo: <b>${p.status}</b></div>`
            },
            { fieldname: "codigo", fieldtype: "Data", label: "Código do Padrão", default: p.codigo, reqd: 1 },
            { fieldname: "descricao", fieldtype: "Data", label: "Descrição", default: p.descricao || "" },
            { fieldname: "validade", fieldtype: "Date", label: "Validade da Calibração", default: p.validade, reqd: 1 },
            { fieldname: "arquivo", fieldtype: "Attach", label: "Arquivo do Padrão (PDF)", reqd: 1 }
        ],
        primary_action_label: "Cadastrar e vincular",
        primary_action: function (values) {
            frappe.call({
                method: "ordem_servico.doc_events.rastreabilidade_padroes.cadastrar_padrao_e_revincular",
                args: {
                    doctype: frm.doc.doctype,
                    name: frm.doc.name,
                    codigo: values.codigo,
                    descricao: values.descricao,
                    validade: values.validade,
                    arquivo: values.arquivo
                },
                freeze: true,
                freeze_message: "Cadastrando padrão e revinculando...",
                callback: function (r) {
                    var res = r.message || {};
                    frappe.show_alert({
                        message: `✅ ${values.codigo} cadastrado como ${res.padrao}`,
                        indicator: "green"
                    });
                    d.hide();
                    _abrir_cadastro_pendente(frm, pendentes, indice + 1);
                }
            });
        },
        secondary_action_label: "Pular",
        secondary_action: function () {
            d.hide();
            _abrir_cadastro_pendente(frm, pendentes, indice + 1);
        }
    });
    d.show();
}
