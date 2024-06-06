from frappe import _, throw
import frappe


def data_limite_pv(doc, pv):
    sales_orders = frappe.get_all("Sales Order", filters={"customer": doc.name}, fields=["name", "status"])
    
    # Verifique se o campo doc.data_limite_de_faturamento não está vazio
    if doc.data_limite_de_faturamento:
        for so in sales_orders:
            
            if so.status not in ["Closed", "Cancelled", "Completed"]:
                # Atualize o campo data_limite_de_faturamento no Sales Order
                frappe.db.set_value("Sales Order", so.name, "data_limite_de_faturamento", doc.data_limite_de_faturamento)


