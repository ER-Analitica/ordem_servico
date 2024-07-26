# -*- coding: utf-8 -*-
# Copyright (c) 2017, laugusto and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

# Custom imports
from datetime import datetime
import time
from frappe.model.document import Document
import frappe
import json
from frappe.utils.data import time_diff, today
from pytz import timezone

'''
@frappe.whitelist()

def get_repair_and_quotation_times(equipment):
    equipment_family = frappe.db.get_value(
        "Modelo Equipamento", {"model": equipment}, ["family_ref"]
    )
    data = frappe.db.get_value(
        "Familias de Equipamentos",
        {"family_name": equipment_family},
        ["quotation_time", "repair_time"],
        as_dict=True,
    )
    return data
'''

@frappe.whitelist()
def make_event(doctype, docname, start_date, start_time, work_time, trigger):
    event = frappe.new_doc("Event")
    event.subject = docname
    event.starts_on = "{} {}".format(start_date, start_time)
    event.ends_on = "{} {}".format(start_date, sum_time(start_time, work_time))
    event.ref_type = doctype
    event.ref_name = docname
    event.save()
    os = frappe.get_doc(doctype, docname)
    if trigger == "quotation":
        os.quotation_event_link = event.name
        os.initial_scheduled_by_name = frappe.get_user().doc.full_name 
        if os.valor and os.peso != "":
            os.valorsaida = os.valor
            os.peso_saida = os.peso
    elif trigger == "repair":
        os.repair_event_link = event.name
        os.final_scheduled_by_name = frappe.get_user().doc.full_name
        os.status_order_service = "Em Conserto"
  
    
    os.save()


@frappe.whitelist()
def get_time_now(doctype, docname, trigger):
    os = frappe.get_doc(doctype, docname)
    if trigger == "start_quotation":
        os.start_quotation_time = time_now()
        os.technical_person_name = frappe.get_user().doc.full_name
        os.status_orcamento = "Iniciado"
    #elif trigger == "schedule_quotation_event":
    elif trigger == "end_quotation":
        os.end_quotation_time = time_now()
        os.tecnico_finalizou = frappe.get_user().doc.full_name
        t1 = os.start_quotation_time
        t2 = os.end_quotation_time
        format = "%d-%m-%Y %H:%M:%S"
        time_diff = datetime.strptime(t2, format) - datetime.strptime(t1, format)
        os.tempo_orcamento = "{}".format(time_diff)
        os.status_orcamento = "Finalizado"
    elif trigger == "start_repair":
        os.start_repair_time = time_now()
        os.repaired_by_name = frappe.get_user().doc.full_name
        os.status_conserto = "Iniciado"
    elif trigger == "end_repair":
        os.end_repair_time = time_now()
        os.repaired_by_name2 = frappe.get_user().doc.full_name
        t1 = os.start_repair_time
        t2 = os.end_repair_time
        format = "%d-%m-%Y %H:%M:%S"
        time_diff = datetime.strptime(t2, format) - datetime.strptime(t1, format)
        os.tempo_conserto = "{}".format(time_diff)
        os.status_conserto = "Finalizado"
        if os.doctype == "Ordem Servico Interna":
             os.status_order_service = "Embalar"
             os.status_faturamento = "Entregar"
        elif os.doctype == "Ordem Servico Externa":
             os.status_order_service = "Encerrada"
        
    os.save()


@frappe.whitelist()
def make_quotation(os_docname):
    os_doc = frappe.get_doc("Ordem Servico Interna", os_docname)
    quot_doc = frappe.new_doc("Quotation")
    quot_doc.os_interna_link = os_doc.name
    quot_doc.defeito_constatado = os_doc.problem_description
    quot_doc.observacao_tecnica = os_doc.problem_observation
    quot_doc.local_manutencao = "Interno"
    quot_doc.party_name = os_doc.customer
    quot_doc.cnpj = frappe.db.get_value("Customer", os_doc.customer, "cnpj")
    quot_doc.numero_serie = os_doc.serie_number
    quot_doc.descricao_equipamento = os_doc.equipment_description
    quot_doc.modalidade_de_entrada = os_doc.modalidade_entrada
    quot_doc.outro = os_doc.outro
    quot_doc.tag = os_doc.equipment_tag
    quot_doc.observacao = os_doc.created_by_observation
    quot_doc.email = frappe.db.get_value(
        "Contacts", {"customer": os_doc.customer}, ["email_id"]
    )
    #inserir contato da os no orç ao gerar orç
    quot_doc.contact_person = os_doc.contact_link
    quot_doc.contact_mobile = os_doc.contact_mobile
    quot_doc.contact_email = os_doc.contact_email
    quot_doc.contact_display = frappe.db.get_value("Contact", os_doc.contact_link, "first_name") + " " + frappe.db.get_value("Contact", os_doc.contact_link, "last_name")
    quot_doc = get_items(os_doc, quot_doc)
    total_rate = get_total(os_doc)
    quot_doc.total = total_rate
    quot_doc.net_total = total_rate
    quot_doc.base_total = total_rate
    quot_doc.base_net_total = total_rate
    quot_doc.base_total_taxes_and_charges = 0
    quot_doc.total_taxes_and_charges = 0
    quot_doc.base_grand_total = 0
    quot_doc.base_rouding_adjustment = 0
    quot_doc.grand_total = 0
    quot_doc.rouding_adjustment = 0
    quot_doc.tc_name = "Boleto 15 dias"
    quot_doc.hash_orc = "1"
    #Trazer cadastro da empresa no cliente ao gerar orçamento
    customer_company = frappe.db.get_value("Customer", quot_doc.party_name, "company")
    if customer_company:
        quot_doc.company = customer_company
   
    
    #quot_doc.terms = frappe.db.get_value(
    #    "Terms and Conditions", {"name": "Boleto 15 dias"}, ["terms"]
    #)
    #Teste chamando detalhes de condições de pagamento cliente
    quot_doc.detalhes_dos_termos_e_condicoes = frappe.db.get_value("Customer", os_doc.customer, "detalhes_dos_termos_e_condicoes")


    quot_doc.conversion_rate = 1
    quot_doc.plc_conversion_rate = 1
    quot_doc.price_list_currency = "BRL"
    quot_doc.hash_gerar_orc = "1"
    return quot_doc
'''
@frappe.whitelist()
def make_nfs(os_docname):
    si_doc = frappe.get_doc("Sales Invoice", os_docname)
    nfs_doc = frappe.new_doc("NFS")
    nfs_doc.customer = si_doc.customer
    nfs_doc.equipment = si_doc.equipment
    nfs_doc.address_display = si_doc.address_display
    nfs_doc.descricao_servico = si_doc.descricao_servico
    nfs_doc.contact_person = si_doc.contact_person
    nfs_doc.customer_address = si_doc.customer_address
    nfs_doc.base_total = si_doc.base_total
    nfs_doc = get_items(si_doc, nfs_doc)

    return nfs_doc
'''
def get_items(os_doc, quot_doc):
    items = os_doc.os_items
    
    for item in items:

        
        selling_price_list = frappe.db.get_value("Quotation", filters={"os_interna_link": "OS-19908"}, fieldname="selling_price_list")
        rate = frappe.get_value("Item Price", filters={"item_code": item.item_code, "price_list": selling_price_list}, fieldname="price_list_rate")
        
        item.item_price = rate


        quot_doc.append(
            
            "items",
            {
                "item_code": item.item_code,
                "qty": item.item_qty,
                "ncm": item.ncm_item,
                "item_name": item.item_name,
                "description": item.item_description,
                "uom": item.uom_item,
                "stock_uom": item.uom_item,
                "qty": item.item_qty,
                "rate":item.item_price,
                "net_rate": item.item_price,
                "base_rate": item.item_price,
                "base_net_rate": item.item_price,
                "amount": item.price_amount,
                "net_amount": item.price_amount,
                "base_amount": item.price_amount,
                "base_net_amount": item.price_amount,
                "conversion_factor": 1,
            },
        )
    return quot_doc


def get_total(os_doc):
    items = os_doc.os_items
    total = 0
    for item in items:
        total += item.price_amount
    return total


def time_now():
    now = datetime.now(timezone("America/Sao_Paulo")).strftime(
        "%d-%m-%Y %H:%M:%S"
    )
    return now


  
def sum_time(t1, t2):
    t1 = time.strptime(str(t1), "%H:%M:%S")
    t2 = time.strptime(str(t2), "%H:%M:%S")
    total_hour = t1.tm_hour + t2.tm_hour
    total_min = t1.tm_min + t2.tm_min
    if total_min >= 60:
        total_hour += 1
        total_min -= 60  # Get minutes difference
    time_object = "{}:{}:00".format(total_hour, total_min)
    return time_object


@frappe.whitelist()
def set_quotation_history(source_docname, source_transaction_date, target_docname):
    os_doc = frappe.get_doc("Ordem Servico Interna", target_docname)
    os_doc.quotation_name = source_docname
    os_doc.quotation_date = source_transaction_date
    os_doc.status_order_service = "Em Aprovação"
    os_doc.save()


@frappe.whitelist()
def set_sales_order_history(source_docname, source_transaction_date, target_docname):
    os_doc = frappe.get_doc("Ordem Servico Interna", target_docname)
    if not os_doc.sales_order_name:
        os_doc.sales_order_name = source_docname
        os_doc.sales_order_date = source_transaction_date
        os_doc.save()


@frappe.whitelist()
def set_sales_invoice_history(source_docname, source_transaction_date, target_docname):
    os_doc = frappe.get_doc("Ordem Servico Interna", target_docname)
    if not os_doc.invoice_name:
        os_doc.invoice_name = source_docname
        os_doc.invoice_date = source_transaction_date
        os_doc.save()


@frappe.whitelist()
def set_payment_entry_history(source_docname, source_transaction_date, target_docname):
    os_doc = frappe.get_doc("Ordem Servico Interna", target_docname)
    if not os_doc.payment_entry_name:
        os_doc.payment_entry_name = source_docname
        os_doc.payment_entry_date = source_transaction_date
        os_doc.save()


@frappe.whitelist()
def set_delivery_note_history(source_docname, source_transaction_date, target_docname):
    os_doc = frappe.get_doc("Ordem Servico Interna", target_docname)
    if not os_doc.delivery_note_name:
        os_doc.delivery_note_name = source_docname
        os_doc.delivery_note_date = source_transaction_date
        os_doc.save()


@frappe.whitelist()
def update_delivery_date(docname, date, reason):
    nowdate = frappe.utils.formatdate(frappe.utils.nowdate(), 'dd-MM-yyyy')
    so = frappe.get_doc('Sales Order', docname)
    so.delivery_date = date
    so.emenda_reason = '{} - {} {}.'.format(reason, frappe.session.user, nowdate)
    so.flags.ignore_validate_update_after_submit = True
    so.flags.ignore_validate = True
    so.save()


@frappe.whitelist()
def make_os(doctype, customer, docname):
    doc = frappe.new_doc(doctype)
    doc.customer = customer
    doc.equipment = docname
    return doc

@frappe.whitelist()
def make_nfs(doctype, customer, docname, address_display, contact_person,contact_email,customer_address,net_total,payment_terms_template, descricao_do_servico):
    doc = frappe.new_doc(doctype)
    doc.customer = customer
    doc.equipment = docname
    doc.address_display = address_display
    doc.descricao_do_servico = descricao_do_servico
    doc.contact_person = contact_person
    doc.contact_email = contact_email
    doc.customer_address = customer_address
    doc.net_total = net_total
    doc.payment_terms_template = payment_terms_template
    #doc.items = items
    return doc
    
    
@frappe.whitelist()
def make_gerar_boleto(doctype, customer, totalliquidoboleto, id_nfs, id_client, equipment, payment_terms_template):
    doc = frappe.new_doc(doctype)
    doc.equipment = equipment
    doc.customer = customer
    doc.totalliquidoboleto = totalliquidoboleto
    doc.id_nfs = id_nfs
    doc.id_client = id_client
    doc.payment_terms_template = payment_terms_template
    #doc.items = items
    return doc





