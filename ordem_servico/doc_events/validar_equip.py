import frappe
from frappe import _

def validate(doc, method):
    if doc.serie_number:
        # Verificar se o serie_number está vinculado ao cliente
        equipment = frappe.db.get_value('Equipamentos', {'name': doc.serie_number, 'customer': doc.customer}, 'name')
        
        if not equipment:
            frappe.throw(_('O número de série do equipamento selecionado não é válido para o cliente selecionado.'))
