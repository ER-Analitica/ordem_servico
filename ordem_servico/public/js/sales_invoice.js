const DocTypes = {
  NFS: 'NFS',
}
frappe.ui.form.on('Sales Invoice', {
  refresh(frm) {
    
    frm.add_custom_button(
      '<i class="fa fa-file-text" aria-hidden="true"></i>  NFS ',
      () => frm.events.make_nfs(frm, DocTypes.NFS),
      'Make'
    )

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
    const { customer, name, address_display, descricao_do_servico, contact_person, contact_email, customer_address, net_total, payment_terms_template, po_no } = frm.doc
    
    // iterar sobre as linhas da tabela filha e pegar as informações do due_date
    let due_dates = ""
    frm.doc.payment_schedule.forEach((row) => {
      const dateParts = row.due_date.split('-'); // divide a data em ano, mês e dia
      const formattedDate = `${dateParts[2]}/${dateParts[1]}/${dateParts[0]}`; // formata a data na ordem desejada
      due_dates += `${formattedDate}\n`; // adiciona a data formatada na lista de datas
    });
  
    frappe.call({
      method: 'ordem_servico.ordem_servico.utils.make_nfs',
      args: {
        doctype: doctype,
        customer: customer,
        docname: name,
        address_display: address_display,
        descricao_do_servico: `${descricao_do_servico}\n\nPedido de Compra n°: ${po_no}\n\nVencimentos:\n${due_dates}\nDados Bancários: \nBANCO ITAU – AG. 0796 – C/C: 06717-1\nBRADESCO – AG. 2830-4 – C/C: 13475-9\nBANCO DO BRASIL – AG. 2766-9 – C/C: 34922-4\nCHAVE PIX/CNPJ: 17358703000199`,
        contact_person: contact_person,
        contact_email: contact_email,
        customer_address: customer_address,
        net_total: net_total,
        payment_terms_template: payment_terms_template,
        po_no: po_no
      },
      callback(r) {
        frappe.model.sync(r.message)
        const { doctype, name } = r.message
        frappe.set_route('Form', doctype, name)
      }
    })
  }
  

})