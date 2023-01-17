import frappe

def execute():
    for item_price in frappe.get_all("Item Price", filters={"selling": 1}):
        frappe.get_doc("Item Price", item_price.name).save()