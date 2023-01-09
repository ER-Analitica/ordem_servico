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
