frappe.ui.form.on('Sales Order', {
  refresh(frm) {
    frm.events.add_custom_button(frm)
  },
  add_custom_button(frm) {
    const overdued = frm.events.overdued()
    if (overdued) {
      frm.add_custom_button(__('Emenda'),
        () => frm.events.update_delivery_date(frm))
    }
  },
  update_delivery_date(frm) {
    frappe.prompt([
        {
          'fieldname': 'new_delivery_date',
          'fieldtype': 'Date',
          'label': 'Data de entrega',
          'reqd': 1
        },
        {
          'fieldname': 'new_delivery_reason',
          'fieldtype': 'Text',
          'label': 'Observação',
          'reqd': 1
        }
      ],
      (data) => {
        const { name } = frm.doc
        frappe.call({
          method: 'ordem_servico.ordem_servico.utils.update_delivery_date',
          args: {
            docname: name,
            date: data.new_delivery_date,
            reason: data.new_delivery_reason
          },
          callback() {
            frappe.show_alert({
              message: 'Emenda concluída!',
              indicator: 'green'
            })
            frm.reload_doc()
          }
        })
      },
      'Digite a nova data de entrega',
      'Salvar'
    )
  },
  overdued() {
    return (
      cur_frm.doc.delivery_date < frappe.datetime.get_today() &&
      cur_frm.doc.delivery_status == 'Not Delivered' &&
      cur_frm.doc.status != 'Closed' &&
      cur_frm.doc.status != 'Cancelled' &&
      cur_frm.doc.status != 'Completed'
    )
  }
})