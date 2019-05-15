# -*- coding: utf-8 -*-
# Copyright (c) 2017, laugusto and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


# Custom imports
import datetime, time
from pytz import timezone


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
    elif trigger == "repair":
        os.repair_event_link = event.name
        os.status_order_service = "Em Conserto"
    os.save()


@frappe.whitelist()
def get_time_now(doctype, docname, trigger):
    os = frappe.get_doc(doctype, docname)
    if trigger == "start_quotation":
        os.start_quotation_time = time_now()
    elif trigger == "end_quotation":
        os.end_quotation_time = time_now()
    elif trigger == "start_repair":
        os.start_repair_time = time_now()
    elif trigger == "end_repair":
        os.end_repair_time = time_now()
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
    quot_doc.customer = os_doc.customer
    quot_doc.numero_serie = os_doc.serie_number
    quot_doc.descricao_equipamento = os_doc.equipment_description
    quot_doc.tag = os_doc.equipment_tag
    quot_doc.email = frappe.db.get_value(
        "Contacts", {"customer": os_doc.customer}, ["email_id"]
    )
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
    quot_doc.terms = frappe.db.get_value(
        "Terms and Conditions", {"name": "Boleto 15 dias"}, ["terms"]
    )
    quot_doc.conversion_rate = 1
    quot_doc.plc_conversion_rate = 1
    quot_doc.price_list_currency = "BRL"
    return quot_doc


def get_items(os_doc, quot_doc):
    items = os_doc.os_items
    for item in items:
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
                "rate": item.item_price,
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
    now = datetime.datetime.now(timezone("America/Sao_Paulo")).strftime(
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
    if not os_doc.quotation_name:
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
def set_reference(target_doctype, target_docname, attr):
    target = frappe.get_doc(target_doctype, target_docname)
    setattr(
        target, attr, target_docname, "Erro ao tentar no atributo ao tentar linkar documentos, atributo: {}".format(attr),
    )
    target.flags.ignore_validate_update_after_submit = True
    target.save()


@frappe.whitelist()
def _make_event(ref_doctype, ref_docname, repair_person=None):
    event = frappe.new_doc("Event")
    event.subject = ref_docname
    event.event_type = "Public"
    event.owner = frappe.session.user
    event.repair_person_name = repair_person
    event.send_reminder = 1
    event.all_day = 1
    event.description = "Manutenção/Calibração - Manutenção: {}".format(ref_docname)
    event.link_documento = ref_doctype
    event.link_dinamico = ref_docname
    event.save()
    set_event_link(ref_doctype, ref_docname, event.name)


def set_event_link(ref_doctype, ref_docname, event_name):
    os = frappe.get_doc(ref_doctype, ref_docname)
    os.event_link = event_name
    os.update_status()


@frappe.whitelist()
def update_delivery_date(docname, date, reason):
    if date < frappe.utils.nowdate():
        frappe.throw('A data {} não pode ser anterior que a atual'.format(date))
    else:
        so = frappe.get_doc('Sales Order', docname)
        so.delivery_date = date
        so.emenda_reason = reason
        so.flags.ignore_validate_update_after_submit = True
        so.save()
