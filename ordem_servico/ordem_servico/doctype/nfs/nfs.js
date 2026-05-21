// Copyright (c) 2022, laugusto and contributors
// For license information, please see license.txt
const DocTypes = {
	boleto: 'Gerar Boleto'
  }
frappe.ui.form.on('NFS', {
	refresh: function(frm) {
		frm.add_custom_button(
			'<i class="fa fa-barcode"></i>  Gerar Boleto',
			() => frm.events.make_gerar_boleto(frm, DocTypes.boleto),
			'Criar'
		)

		if (frm.doc.id_nfs && frm.doc.docstatus === 1) {
			frm.add_custom_button('Atualizar Status da Nota', () => {
				frappe.call({
					method: 'ordem_servico.ordem_servico.doctype.nfs.nfs.atualizar_status_nota',
					args: { docname: frm.doc.name },
					callback(r) {
						frappe.show_alert({ message: `Status: ${r.message}`, indicator: 'green' })
						frm.reload_doc()
					}
				})
			})
		}

	},


	make_gerar_boleto(frm, doctype) {
		const { customer, name,  totalliquidoboleto, id_nfs, id_client, equipment, payment_terms_template } = frm.doc
		frappe.call({
		  method: 'ordem_servico.ordem_servico.utils.make_gerar_boleto',
		  args: {
			doctype: doctype,
			customer: customer,
			docname: name,
			totalliquidoboleto: totalliquidoboleto,
			id_nfs: id_nfs,
			id_client: id_client,
			equipment: equipment,
			payment_terms_template: payment_terms_template
			/*items: items*/
		  },
		  callback(r) {
			frappe.model.sync(r.message)
			const { doctype, name } = r.message
			frappe.set_route('Form', doctype, name)
		  }
		})
	  }
	



});
