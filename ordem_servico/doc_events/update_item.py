import frappe

def on_update(self, method):
    if not self.selling:
        return
    frappe.db.set_value("Item",self.item_code,"standard_rate",self.price_list_rate)
