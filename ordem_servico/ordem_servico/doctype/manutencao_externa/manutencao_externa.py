# -*- coding: utf-8 -*-
# Copyright (c) 2019, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

from enum import Enum


class ManutencaoExterna(Document):
    pass


PENDING = "Pendente"
SUCCEEDED = "Concluído"
CANCELLED = "Cancelado"


@frappe.whitelist()
def make_maintenance(docname):
    os = frappe.get_doc("Ordem Servico Externa", docname)
    os_name = os.name

    def _make_maintenance(equipment, docname):
        maint = frappe.new_doc("Manutencao Externa")
        maint.naming_series = "MANUT-{}-.#".format(os.name)
        maint.workflow_state = PENDING
        maint.customer = os.customer
        maint.serie = equipment.serie
        maint.tag = equipment.tag
        maint.model = equipment.model
        maint.description = equipment.description
        maint.os_link = os_name
        maint.save()
        return maint

    def update_maint_status(equipment, maint):
        equipment.maint_status = maint.workflow_state

    def update_maint_link(equipment, maint):
        equipment.maint_link = maint.name

    for equipment in os.os_equipments:
        maint = _make_maintenance(equipment, os_name)
        update_maint_status(equipment, maint)
        update_maint_link(equipment, maint)

    os.update_status()
    os.flags.ignore_validate_update_after_submit = True
    os.save()
    return

