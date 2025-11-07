import frappe
from frappe import _

def validacao_cadastro_equip(doc, method):
    if frappe.db.exists(
        "Equipamentos",
        {
            "numero_serie": doc.numero_serie,
            "descricao": doc.descricao,
            "modelo_equipamento": doc.modelo_equipamento,
        },
    ):
        frappe.throw("Já existe um equipamento cadastrado com esses mesmos dados.")