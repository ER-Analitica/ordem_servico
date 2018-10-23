// Copyright (c) 2018, laugusto and contributors
// For license information, please see license.txt

{% include "ordem_servico/public/js/ordem_servico.js" %}


frappe.ui.form.on('Ordem Servico Externa', {
	
	create_quotation: function () {

		if (cur_frm.doc.__unsaved) {
			frappe.throw('Favor salvar documento!');
		}
		frappe.call({
			method: 'ordem_servico.ordem_servico.utils.make_quotation',
			args: {
				doctype: frm.doc.doctype,
				docname: frm.doc.name,
				local: 'Externo',
			},
		});
		frm.reload_doc();
		show_alert('Orçamento gerado.');
	},

	schedule_visit: function () {

		if (cur_frm.doc.__unsaved) {
			frappe.throw('Favor salvar documento!');
		}
		frappe.call({
			method: 'ordem_servico.ordem_servico.utils.make_event',
			args: {
				doctype: frm.doc.doctype,
				docname: frm.doc.name,
				start_date: frm.doc.visit_schedule_date,
				start_time: frm.doc.visit_schedule_time,
				work_time: frm.doc.repair_time,
			},
		});
		frm.reload_doc();
		show_alert('Visita agendada.');
	},



});
