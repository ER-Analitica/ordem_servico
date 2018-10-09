# -*- coding: utf-8 -*-
# Copyright (c) 2017, laugusto and contributors
# For license information, please see license.txt
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

import datetime
import time
import json, os
from six import iteritems, string_types, integer_types


@frappe.whitelist()
def purposes_rename(maint_name):
    maint = frappe.get_doc("Maintenance Visit", maint_name)
    len_array_purposes = len(maint.purposes)
    idx = 0
    if maint.local_manutencao == "Externo":
        local_manutencao = "EXT"
    else:
        local_manutencao = "INT"
    for idx in range(len_array_purposes):
        maint.purposes[idx].os = "OS-%s/%s" % (local_manutencao, str(idx))
    maint.save()
    return


@frappe.whitelist()
def new_quotation(maint_name, purposes_idx):
    maint = frappe.get_doc("Maintenance Visit", maint_name)
    idx = int(purposes_idx) - 1

    # Create quotation doc
    quotation = frappe.new_doc("Quotation")
    quotation.os_doctype = "Maintenance Visit"
    if maint.local_manutencao == 'Interno':
        quotation.observacao_tecnica = maint.purposes[idx - 1].observacao_3
        quotation.defeito_constatado = maint.purposes[idx - 1].defeito_constatado2
    elif maint.local_manutencao == 'Externo':
        quotation.observacao_tecnica = maint.purposes[idx - 1].observacao_2
        quotation.defeito_constatado = maint.purposes[idx - 1].defeito_constatado
    quotation.os_link = maint.name
    quotation.local_manutencao = maint.local_manutencao
    quotation.customer = maint.customer_name
    quotation.numero_serie = maint.purposes[idx - 1].numero_serie
    quotation.descricao_equipamento = maint.purposes[idx - 1].item_name
    quotation.tag = maint.purposes[idx - 1].tag
    quotation.email = frappe.db.get_value('Contacts', {'customer': quotation.customer}, ['email_id'])
    date = datetime.date.today() + datetime.timedelta(days=15)
    quotation.valid_till = date.strftime('%y-%m-%d')
    quotation.tc_name = "Boleto 15 dias"
    quotation.terms = frappe.db.get_value(
        'Terms and Conditions', {'name': 'Boleto 15 dias'}, ['terms'])
    quotation.conversion_rate = 1
    quotation.plc_conversion_rate = 1
    quotation.price_list_currency = "BRL"
    quotation.flags.ignore_mandatory = True
    quotation.flags.ignore_validate = True
    quotation.save()

    # Set quotation name to purposes os
    date_now = datetime.datetime.today().strftime('%Y-%m-%d')
    maint.purposes[idx - 1].status_ordem_servico = "Em Aprovação"
    maint.purposes[idx - 1].documento_orcamento = quotation.name
    maint.purposes[idx - 1].numero_orcamento = quotation.name
    maint.purposes[idx - 1].data_orcamento2 = date_now
    maint.purposes[idx - 1].data_orcamento = date_now
    maint.save()
    return quotation


@frappe.whitelist()
def make_event(doc_name):
    maint = frappe.get_doc("Maintenance Visit", doc_name)
    purposes = maint.purposes

    for row in purposes:

        # Create first event
        if (not row.evento_link and row.agendado_para):
            event = frappe.new_doc("Event")
            event.subject = row.os
            event.starts_on = '{} {}'.format(row.data_agendamento_orcamento, row.hora_agendamento_orcamento)
            event.ends_on = '{} {}'.format(row.data_agendamento_orcamento, sum_hours(row.hora_agendamento_orcamento, row.tempo_orcamento))
            event.manutencao = maint.name
            event.tipo_agenda = 'Orçamento'
            event.ordem_servico = row.os
            event.equipamento = row.modelo_equipamento
            event.descricao = row.item_name
            event.tag = row.tag
            event.tempo_orcamento_conserto = row.tempo_orcamento
            event.ref_type = "Maintenance Visit Purpose"
            event.save()
            row.status_ordem_servico = 'Em Orçamento'
            row.data_agendamento_orcamento = datetime.datetime.today(
            ).strftime('%Y-%m-%d')
            row.evento_link = event.name
            row.save()

        # Create second event
        elif (not row.evento_link2 and row.agendado_para2):
            event = frappe.new_doc("Event")
            event.subject = row.os
            event.starts_on = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:00")
            event.ends_on = datetime.datetime.now().strftime(
                "%Y-%m-%d 18:00:00")
            event.manutencao = maint.name
            event.tipo_agenda = 'Manutenção'
            event.ordem_servico = row.os
            event.starts_on = '{} {}'.format(row.data_agendamento_conserto, row.hora_agendamento_conserto)
            event.ends_on = '{} {}'.format(row.data_agendamento_conserto, sum_hours(row.hora_agendamento_conserto, row.tempo_conserto)) # Sum start maintenance and maintenance time
            event.equipamento = row.modelo_equipamento
            event.descricao = row.item_name
            event.tag = row.tag
            event.tempo_orcamento_conserto = row.tempo_conserto
            event.ref_type = "Maintenance Visit Purpose"
            event.save()
            row.status_ordem_servico = 'Em Conserto'
            row.data_agendamento_orcamento = datetime.datetime.today(
            ).strftime('%Y-%m-%d')
            row.evento_link2 = event.name
            row.save()


def sum_hours(t1, t2):
    t1 = time.strptime(str(t1), '%H:%M:%S')
    t2 = time.strptime(str(t2), '%H:%M:%S')
    total_hour = t1.tm_hour + t2.tm_hour
    total_min = t1.tm_min + t2.tm_min
    if int(total_min) >= 60:
        total_hour += 1
        total_min -= 60 # Get minutes difference
    time_object = '{}:{}:00'.format(total_hour, total_min)
    return time_object


@frappe.whitelist()
def custom_get_value(doctype,
                     fieldname,
                     filters=None,
                     as_dict=True,
                     debug=False,
                     parent=None):
    try:
        filters = json.loads(filters)

        if isinstance(filters, (integer_types, float)):
            filters = frappe.as_unicode(filters)

    except (TypeError, ValueError):
        # filters are not passesd, not json
        pass

    try:
        fieldname = json.loads(fieldname)
    except (TypeError, ValueError):
        # name passed, not json
        pass

    # check whether the used filters were really parseable and usable
    # and did not just result in an empty string or dict
    if not filters:
        filters = None

    return frappe.db.get_value(
        doctype, filters, fieldname, as_dict=as_dict, debug=debug)


@frappe.whitelist()
def get_tempo_orcamento_conserto(equipamento):
    familia = frappe.db.get_value('Equipamentos', {'name': equipamento},
                                  ['familia'])
    data = frappe.db.get_value(
        'Familias de Equipamentos', {'name': familia},
        ['tempo_orcamento', 'tempo_conserto'],
        as_dict=True)
    return data


@frappe.whitelist()
def next_contact(doc_name):
    quotation = frappe.get_doc('Quotation', doc_name)
    if quotation.local_manutencao == 'Interno' and not quotation.proximo_contato:
        event = frappe.new_doc('Event')
        event.all_day = 0
        event.creation = datetime.datetime.now()
        event.description = "Contact {} By : {} To Discuss : {}".format(quotation.customer, quotation.modified_by, quotation.name)
        event.event_type = "Public"
        event.name = 'EV#####'
        event.owner = quotation.modified_by
        event.ref_type = 'Quotation'
        event.ref_name = quotation.name
        event.send_reminder = 1
        date = datetime.datetime.now() + datetime.timedelta(days=1)
        event.starts_on = date.strftime('%Y-%m-%d %H:%M:00')
        event.subject = 'Contact {}'.format(quotation.customer)
        event.save()

        quotation.ref_type = 'Event'
        quotation.ref_name = event.name
        quotation.save()