/*const DocTypes = {
    NFS: 'NFS'
}
  
  frappe.ui.form.on('Sales Invoice', {
    refresh(frm) {
      frm.add_custom_button(
        'NFS',
        () => frm.events.make_nfs(frm, DocTypes.NFS),
        'Make'
      )
    },
    make_nfs(frm, doctype) {
      const { customer, name } = frm.doc
      frappe.call({
        method: 'ordem_servico.ordem_servico.utils.make_nfs',
        args: {
          doctype: doctype,
          customer: customer,
          docname: name
        },
        callback(r) {
          frappe.model.sync(r.message)
          const { doctype, name } = r.message
          frappe.set_route('Form', doctype, name)
        }
      })
    }
  })*/