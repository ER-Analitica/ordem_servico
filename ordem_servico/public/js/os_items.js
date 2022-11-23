frappe.ui.form.on('Ordem Servico Items', {
  item_code(frm, cdt, cdn) {
    const d = locals[cdt][cdn]
    d.item_qty = 1
    d.price_amount = d.item_qty * d.item_price
    frm.refresh_field('os_items')
  },
  item_qty(frm, cdt, cdn) {
    const d = locals[cdt][cdn]
    d.price_amount = d.item_qty * d.item_price
    frm.refresh_field('os_items')
  }
})

