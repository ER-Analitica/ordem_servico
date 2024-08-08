from __future__ import unicode_literals

import frappe


def on_submit(doc, method):
     
    try:
        if doc.ordem_servico == "Ordem Servico Externa":
            count = 0
            while count < int(doc.quantidade):
                os = frappe.new_doc(doc.ordem_servico)
                os.customer = doc.cliente
                #os.equipment_location = doc.loc_equip
                os.contact_link = doc.contato
                #os.has_quotation_link = doc.orcamento
                #os.have_quotation = doc.possui_orcamento
                os.status_order_service = doc.status_order_service
                os.sales_order_reference = doc.sales_order_reference
                os.save()
                count += 1
        elif doc.ordem_servico == "Ordem Servico Interna":
            count = 0
            while count < int(doc.quantidade):
                os = frappe.new_doc(doc.ordem_servico)
                os.customer = doc.cliente
                os.equipment_location = doc.loc_equip
                os.contact_link = doc.contato
                os.has_quotation_link = doc.orcamento
                os.have_quotation = doc.possui_orcamento
                os.status_order_service = doc.status_order_service_interna
                os.modalidade_entrada = doc.modalidade_entrada
                os.nome_transportadora_entrada = doc.nome_transportadora_entrada
                os.outro = doc.outro
                os.base_total = doc.base_total
                os.entry_date = doc.entry_date
                os.entry_sales_invoice = doc.entry_sales_invoice
                os.valor = doc.valor
                os.peso = doc.peso
                os.initial_scheduled_to = doc.initial_scheduled_to
                os.initial_scheduled_to_name = doc.initial_scheduled_to_name
                os.initial_scheduled_by_name = doc.initial_scheduled_by_name
                os.quotation_schedule_date = doc.quotation_schedule_date
                os.quotation_schedule_time = doc.quotation_schedule_time
                os.quotation_time = doc.quotation_time
                os.quotation_event_link = doc.quotation_event_link   
                os.os_items = doc.os_items
                os.pontos_cal_criterios_aceitacao = doc.pontos_cal_criterios_aceitacao
                os.final_scheduled_to = doc.final_scheduled_to
                os.final_scheduled_to_name = doc.final_scheduled_to_name
                os.final_scheduled_by_name = doc.final_scheduled_by_name
                os.repair_schedule_date = doc.repair_schedule_date
                os.repair_schedule_time = doc.repair_schedule_time
                os.repair_time = doc.repair_time
                os.repair_event_link = doc.repair_event_link
                os.save()
                count += 1
        
    except:
        frappe.throw("Ocorreu algum erro durante a criação em lote")
