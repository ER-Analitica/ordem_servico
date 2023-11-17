# -*- coding: utf-8 -*-
# Copyright (c) 2018, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from datetime import datetime
from frappe.model.document import Document
from frappe.contacts.doctype.address.address import get_address_display
from frappe.utils.data import time_diff, today
from pytz import timezone



def data_now():
	data_hora = datetime.now(timezone("America/Sao_Paulo"))
	formato = "%d/%m/%Y %H:%M:%S"
	return data_hora.strftime(formato)

class OrdemServicoInterna(Document):
	

	def validate(self):	
		#address = frappe.get_doc("Address", self.address_os)
		#self.address_display = get_address_display(address)
		if self.equipment:
			self.update_equipamento()

			
		#verificar campos preenchidos na os para passar de status
		'''	
		if self.customer and self.contact_link and self.cfop and self.ncm and self.serie_number and self.equipment_model and self.equipment_tag and self.equipment_description and self.tipo_servico != "" :

			
			#self.tempo_final_recebimento = data_now()
			#time_diff = datetime.strptime(self.tempo_final_recebimento, format) - datetime.strptime(self.tempo_inicio_recebimento, format)
			#t1 = self.tempo_final_recebimento
			#t2 = self.tempo_inicio_recebimento
			format = "%d/%m/%Y %H:%M:%S"
			#time_diff = datetime.strptime(t1, format) - datetime.strptime(t2, format)
			#self.tempo_em_recebimento = "{}".format(time_diff)
			#self.status_order_service = "Aguardando Orçamento"
		#else:
			#self.status_order_service = "Em Recebimento"


		if self.status_order_service == "Em Recebimento":
			frappe.msgprint('Alguns campos precisam ser preenchidos antes de passarmos para o próximo status!');
		'''

		#agendamento inicial
		#eval: doc.customer && doc.contact_link && doc.cfop && doc.ncm && doc.serie_number && doc.equipment_model && doc.equipment_tag && doc.equipment_description && doc.tipo_servico
		
		


	def update_equipamento(self):
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "serie_number", self.get('serie_number'))
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "equipment_model", self.get('equipment_model'))
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "tag", self.get('equipment_tag'))
		frappe.db.set_value("Equipamentos do Cliente", self.equipment, "description", self.get('equipment_description'))
		frappe.db.commit()

	def validate(self):
		if self.sem_conserto == 1 and self.status_order_service == "Encerrada":
			self.status_order_service == "Encerrada"
		elif self.sem_conserto == 1:
			self.quotation_status = "Concluído"
			self.status_order_service = "Embalar"
		if self.have_quotation == 1:
			self.quotation_status = "Concluído"
		#if self.status_order_service == "Embalar":
			#self.status_faturamento = "Entregar"
	
	

	



	


	

	

