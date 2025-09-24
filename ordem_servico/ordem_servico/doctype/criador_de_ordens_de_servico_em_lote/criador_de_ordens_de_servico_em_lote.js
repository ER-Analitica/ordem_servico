frappe.ui.form.on('Criador de Ordens de Servico em Lote', {
    refresh: function(frm) {
        cur_frm.fields_dict.contato.get_query = () => {
            return {
                filters: {
                    'link_doctype': 'Customer', // ou 'Company', dependendo do vínculo
                    'link_name': cur_frm.doc.cliente // ou cur_frm.doc.company
                }
            }
        }
		cur_frm.fields_dict.responsavel_tecnico_user.get_query = () => {
			return {
				filters: {
					'role_profile_name': ['in', ['Diretor Executivo', 'Supervisor Técnico', 'Assistente Técnico em Eletrônica', 'Estágiário Técnico', 'Gerente Técnico', 'Coordenador Técnico', 'Técnico em Eletrônica Senior', 'Técnico em Eletrônica Pleno', 'Técnico em Eletrônica Junior', 'Diretor Técnico']],
					'enabled': '1'
				}
			}
		}
    },
	
	schedule_quotation_event(frm) {
		const { __unsaved } = cur_frm.doc
		if (__unsaved) {
		  frappe.throw('Favor salvar documento!')
		}
		const {
		  doctype,
		  name,
		  quotation_schedule_date,
		  quotation_schedule_time,
		  quotation_time
		} = frm.doc
		frappe.call({
		  method: 'ordem_servico.ordem_servico.utils.make_event',
		  args: {
			doctype: doctype,
			docname: name,
			start_date: quotation_schedule_date,
			start_time: quotation_schedule_time,
			work_time: quotation_time,
			trigger: 'quotation'
		  },
		  callback(res){
			show_alert('Orçamento agendado.')
			frm.reload_doc()
		  }
		  
		})
	  },

	  schedule_repair_event(frm) {
		const { __unsaved } = cur_frm.doc
		if (__unsaved) {
		  frappe.throw('Favor salvar documento!')
		}
		const {
		  doctype,
		  name,
		  repair_schedule_date,
		  repair_schedule_time,
		  repair_time
		} = frm.doc
		frappe.call({
		  method: 'ordem_servico.ordem_servico.utils.make_event',
		  args: {
			doctype: doctype,
			docname: name,
			start_date: repair_schedule_date,
			start_time: repair_schedule_time,
			work_time: repair_time,
			trigger: 'repair'
		  },
		  callback(res){
			show_alert('Conserto agendado.')
			frm.reload_doc()
		  }
		})
	  },

	  orcamento: function(frm) {
		// Obter o valor do campo "has_quotation_link"
		const quotation = frm.doc.orcamento;
	
		// Limpar a tabela se o campo "has_quotation_link" estiver vazio
		if (!quotation) {
		  frm.clear_table('os_items');
		  frm.refresh_field('os_items');
		  return;
		}
	
		// Consultar a tabela de orçamento usando o valor do campo "has_quotation_link"
		frappe.call({
		  method: 'frappe.client.get',
		  args: {
			doctype: 'Quotation',
			name: quotation,
		  },
		  callback: function(response) {
			const quotation_doc = response.message;
	
			// Limpar a tabela antes de adicionar novos itens
			frm.clear_table('os_items');
	
			// Iterar sobre os itens do orçamento e adicionar à tabela em Ordem Servico Interna
			if (quotation_doc && quotation_doc.items) {
			  for (const item of quotation_doc.items) {
				const row = frm.add_child('os_items');
				row.item_code = item.item_code;
				row.item_name = item.item_name;
				row.item_qty = item.qty;
				// Adicione outros campos necessários aqui
			  }
			  frm.refresh_field('os_items');
			}
		  },
		});
	  },
	
});
