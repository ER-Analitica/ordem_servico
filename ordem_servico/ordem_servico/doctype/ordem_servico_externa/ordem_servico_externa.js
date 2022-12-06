// Copyright (c) 2018, laugusto and contributors
// For license information, please see license.txt

{% include "ordem_servico/public/js/ordem_servico.js" %}

frappe.ui.form.on('Ordem Servico Externa', {
	create_quotation(frm) {
		const { __unsaved } = cur_frm.doc
		if (__unsaved) {
			frappe.throw('Favor salvar documento!')
		}
		const { doctype, name } = frm.doc
		frappe.call({
			method: 'ordem_servico.ordem_servico.utils.make_quotation',
			args: {
				doctype: doctype,
				docname: name,
				local: 'Externo'
			}
		})
		frm.reload_doc()
		show_alert('Orçamento gerado.')
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
			}
		})
		frm.reload_doc()
		show_alert('Visita agendada.')
	},
	end_repair(frm) {
		const { __unsaved, quotation_status } = cur_frm.doc
		if (__unsaved) {
			frappe.throw('Favor salvar documento!')
		}  
		/*else if (!quotation_status) {
			frappe.throw('Favor colocar Status do Orçamento!')
		}*/
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
	},
	equipment(frm){
		if (!frm.doc.equipment) return;
		frappe.model.get_value("Equipamentos do Cliente", 
		frm.doc.equipment, ["serie_number", "equipment_model", "tag", "description"], 
		function(res){
		[["serie_number","serie_number"], 
		["equipment_model", "equipment_model"], 
		["tag", "equipment_tag"], 
		["description", "equipment_description"]].forEach(kv => {
		frm.set_value(kv[1], res[kv[0]]);
	  })
	  })
	}
})
