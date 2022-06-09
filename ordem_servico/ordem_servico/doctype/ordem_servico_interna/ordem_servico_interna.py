# -*- coding: utf-8 -*-
# Copyright (c) 2018, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class OrdemServicoInterna(Document):
	def on_update(self):
		if self.equipment:
			self.update_equipamento()
	def update_equipamento(self):
		equipamento = frappe.get_doc("Equipamentos do Cliente",self.equipment)
		equipamento.update({
			"serie_number": self.serie_number,
    		"equipment_model": self.equipment_model,
			"tag": self.equipment_tag,
			"description": self.equipment_description
		})
		equipamento.save()
	
