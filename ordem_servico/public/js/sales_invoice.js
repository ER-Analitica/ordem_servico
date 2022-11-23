const DocTypes = {
  NFS: 'NFS'
}
frappe.ui.form.on('Sales Invoice', {
  refresh(frm) {
    /*
    frm.add_custom_button(
      'NFS',
      () => frm.events.make_nfs(frm, DocTypes.NFS),
      'Make'
    )*/
  },
  after_save(frm) {
    //Set Sales Invoice on OS History section
    if (frm.doc.os_interna_link) {
      const { name, posting_date, os_interna_link } = frm.doc
      frappe.call({
        method: 'ordem_servico.ordem_servico.utils.set_sales_invoice_history',
        args: {
          source_docname: name,
          source_transaction_date: posting_date,
          target_docname: os_interna_link
        }
      })
    }
  },
  /*doc.customer = customer
  doc.equipment = docname
  doc.address_display = address_display
  doc.descricao_servico = descricao_servico
  doc.contact_person = contact_person
  doc.contact_email = contact_email
  doc.customer_address = customer_address
  doc.base_total = base_total*/
  make_nfs(frm, doctype) {
    const { customer, name, address_display, descricao_servico, contact_person, contact_email, customer_address, base_total } = frm.doc
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.make_nfs',
      args: {
        doctype: doctype,
        customer: customer,
        docname: name,
        address_display: address_display,
        descricao_servico: descricao_servico,
        contact_person: contact_person,
        contact_email: contact_email,
        customer_address: customer_address,
        base_total: base_total
        /*items: items*/
      },
      callback(r) {
        frappe.model.sync(r.message)
        const { doctype, name } = r.message
        frappe.set_route('Form', doctype, name)
      }
    })
  }

})



