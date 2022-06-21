# -*- coding: utf-8 -*-
# Copyright (c) 2018, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class OrdemServicoExterna(Document):
	def validate(self):
		if self.equipment:
			self.update_equipamento()
	def update_equipamento(self):
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "serie_number", self.get('serie_number'))
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "equipment_model", self.get('equipment_model'))
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "tag", self.get('equipment_tag'))
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "description", self.get('equipment_description'))
		frappe.db.commit()


