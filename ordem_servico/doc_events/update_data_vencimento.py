from xml.dom.minidom import Document
from frappe import _, throw
import frappe


def update_data_vencimento(doc, method):
    opportunity = frappe.get_doc("Opportunity", doc.reference_name)
    data_vencimento = frappe.get_list("Data de Vencimento Taks", filters={"parent": opportunity.name, "reference_task": doc.name})

    if doc.status == "Closed":
        if data_vencimento:
            frappe.delete_doc("Data de Vencimento Taks", data_vencimento[0].name)
            frappe.publish_realtime("doc_update", {"doctype": "Opportunity", "name": opportunity.name})
          
    else:
        if data_vencimento:
            if data_vencimento[0].data_vencimento != doc.date:
                data_vencimento = frappe.get_doc("Data de Vencimento Taks", data_vencimento[0].name)
                data_vencimento.data_vencimento = doc.date
                data_vencimento.save()
                frappe.publish_realtime("doc_update", {"doctype": "Opportunity", "name": opportunity.name})

                
                
            
        else:
            data_vencimento = frappe.get_doc({
                "doctype": "Data de Vencimento Taks",
                "parent": opportunity.name,
                "parentfield": "data_de_vencimento_das_tarefas",
                "parenttype": "Opportunity",
                "data_vencimento": doc.date,
                "reference_task": doc.name
            })
            data_vencimento.save()
            frappe.publish_realtime("doc_update", {"doctype": "Opportunity", "name": opportunity.name})

