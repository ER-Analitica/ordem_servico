# -*- coding: utf-8 -*-
# Copyright (c) 2022, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

from datetime import datetime
import time
import frappe
import requests
import json
from frappe.utils.data import time_diff, today
from pytz import timezone

from frappe.model.document import Document

#Criar nfs

def _extract_code(value):
    if value and " - " in value:
        return value.split(" - ")[0].strip()
    return value or ""

def _format_description(text):
    return text or ""

ASAAS_TOKEN = "$aact_hmlg_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmEwZDhkY2UzLWYwYjEtNDY1Zi1iMDc2LTY3NDEwOTAzZTkwNTo6JGFhY2hfM2M3ZmRmYzktM2EzOS00NWNjLTgwMjgtZmU3ZjU0Y2JlMTZl"
ASAAS_SANDBOX = True  # Alterar para False ao ir para produção
ASAAS_BASE_URL = "https://api-sandbox.asaas.com/v3" if ASAAS_SANDBOX else "https://api.asaas.com/v3"

class NFS(Document):

	def before_save(self):
			
		if self.situacao_nota == "Agendada":
			global retencao_imposto

			retention_type_map = {
				"Não Retido": "NOT_WITHHELD",
				"Retido": "WITHHELD"
			}
			tax_status_map = {
				"00": "NONE",
				"01": "STANDARD_TAXABLE_OPERATION",
				"02": "DIFFERENTIATED_RATE_TAXABLE_OPERATION",
				"03": "TAXABLE_PER_MEASURE_UNIT_OPERATION",
				"04": "MONOPHASIC_RESALE_ZERO_RATE_OPERATION",
				"05": "TAX_SUBSTITUTION_OPERATION",
				"06": "ZERO_RATE_TAXABLE_OPERATION",
				"07": "EXEMPT_CONTRIBUTION_OPERATION",
				"08": "NON_TAXABLE_OPERATION",
				"09": "TAX_SUSPENSION_OPERATION",
				"49": "OTHER_OUTPUT_OPERATION",
				"50": "CREDITABLE_EXCLUSIVE_TAXED_DOMESTIC_REVENUE_OPERATION",
				"51": "CREDITABLE_EXCLUSIVE_NON_TAXED_DOMESTIC_REVENUE_OPERATION",
				"52": "CREDITABLE_EXPORT_REVENUE_OPERATION",
				"53": "CREDITABLE_TAXED_AND_NON_TAXED_DOMESTIC_REVENUE_OPERATION",
				"54": "CREDITABLE_TAXED_DOMESTIC_AND_EXPORT_REVENUE_OPERATION",
				"55": "CREDITABLE_NON_TAXED_DOMESTIC_AND_EXPORT_REVENUE_OPERATION",
				"56": "CREDITABLE_TAXED_AND_NON_TAXED_DOMESTIC_AND_EXPORT_REVENUE_OPERATION",
				"60": "PRESUMED_CREDIT_EXCLUSIVE_TAXED_DOMESTIC_REVENUE_OPERATION",
				"61": "PRESUMED_CREDIT_EXCLUSIVE_NON_TAXED_DOMESTIC_REVENUE_OPERATION",
				"62": "PRESUMED_CREDIT_EXCLUSIVE_EXPORT_REVENUE_OPERATION",
				"63": "PRESUMED_CREDIT_TAXED_AND_NON_TAXED_DOMESTIC_REVENUE_OPERATION",
				"64": "PRESUMED_CREDIT_TAXED_DOMESTIC_AND_EXPORT_REVENUE_OPERATION",
				"65": "PRESUMED_CREDIT_NON_TAXED_DOMESTIC_AND_EXPORT_REVENUE_OPERATION",
				"66": "PRESUMED_CREDIT_TAXED_AND_NON_TAXED_DOMESTIC_AND_EXPORT_REVENUE_OPERATION",
				"67": "PRESUMED_CREDIT_OTHER_OPERATION",
				"70": "ACQUISITION_WITHOUT_CREDIT_RIGHT_OPERATION",
				"71": "ACQUISITION_WITH_EXEMPTION_OPERATION",
				"72": "ACQUISITION_WITH_SUSPENSION_OPERATION",
				"73": "ACQUISITION_ZERO_RATE_OPERATION",
				"74": "ACQUISITION_WITHOUT_CONTRIBUTION_OPERATION",
				"75": "ACQUISITION_BY_TAX_SUBSTITUTION_OPERATION",
				"98": "OTHER_INPUT_OPERATION",
				"99": "OTHER_OPERATION",
			}

			if retention_type_map.get(self.pis_cofins_retention_type) == "WITHHELD":
				if not self.pis_cofins_tax_status:
					frappe.throw("Selecione a Situação Tributária do PIS/COFINS — obrigatória quando o tipo de retenção for 'Retido'")
			if self.imposto_retido == "Prestador de serviço - Eu recolho o ISS":
				retencao_imposto = False
			else:
				retencao_imposto = True
				totaliss = self.net_total * frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "aliquota") / 100
				self.totalliquido = totaliss
		
			#listar cliente
			url = f"{ASAAS_BASE_URL}/customers?cpfCnpj="+str(frappe.db.get_value("Customer", self.customer, "cnpj"))
			payload={}
			headers = {
			'Content-Type': 'application/json',
			'access_token': ASAAS_TOKEN,
			'Cookie': 'AWSALB=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBCORS=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBTG=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; AWSALBTGCORS=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
			}

			response = requests.request("GET", url, headers=headers, data=payload)
			
			print(response.text)
			datajson = json.loads(response.text)
			self.client_exist = datajson.get("totalCount")	

			#Cliente não existe
			if self.client_exist == 0:
			
				#criar cliente 
				url = f"{ASAAS_BASE_URL}/customers"

				payload = json.dumps({
							"name": frappe.db.get_value("Customer", self.customer, "customer_name"),
							"email": self.contact_email,
							"phone": frappe.db.get_value("Contact", self.contact_person, "phone"),
							"mobilePhone": frappe.db.get_value("Contact", self.contact_person, "mobile_no"),
							"cpfCnpj": frappe.db.get_value("Customer", self.customer, "cnpj"),
							"postalCode": frappe.db.get_value("Address", self.customer_address, "cep"),
							"address": frappe.db.get_value("Address", self.customer_address, "address_line1"),
							"addressNumber": frappe.db.get_value("Address", self.customer_address, "numero"),
							"complement": frappe.db.get_value("Address", self.customer_address, "address_line2"),
							"province": frappe.db.get_value("Address", self.customer_address, "bairro"),
							"notificationDisabled": False
							})
				headers = {
							'Content-Type': 'application/json',
							'access_token': ASAAS_TOKEN,
							'Cookie': 'AWSALB=NDsZE6HSGykB5Q/ryMenP5mW4vs3e+cc2Ed+0RscpplUQ/9TphPnQhYnPH5iTM59Ddtpm9FrWGyy+q4cikvIQw2eggvGHPUAB2Q47Iz7FzPK1LpaCMFmK1FbDYLu; AWSALBCORS=NDsZE6HSGykB5Q/ryMenP5mW4vs3e+cc2Ed+0RscpplUQ/9TphPnQhYnPH5iTM59Ddtpm9FrWGyy+q4cikvIQw2eggvGHPUAB2Q47Iz7FzPK1LpaCMFmK1FbDYLu; AWSALBTG=cuofeg0H83YZQFE3ZHLeoAlPHCxQbHHVpYfQWxHhrWZuWPbj5nhcbjhbziMSqKF7zqkPW+pg3HhCJQInzc5KFkGip1Fr+gXZ/1Ql1PSdeG31RpnqjZSrjvMCxtCh8kSi/VQof4lxksWUlJ9YdvgVn+DY5qLXIMsCLJ4sPHzFyTfJ; AWSALBTGCORS=cuofeg0H83YZQFE3ZHLeoAlPHCxQbHHVpYfQWxHhrWZuWPbj5nhcbjhbziMSqKF7zqkPW+pg3HhCJQInzc5KFkGip1Fr+gXZ/1Ql1PSdeG31RpnqjZSrjvMCxtCh8kSi/VQof4lxksWUlJ9YdvgVn+DY5qLXIMsCLJ4sPHzFyTfJ; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
							}

				response = requests.request("POST", url, headers=headers, data=payload)

				print(response.text)
				datajson = json.loads(response.text)
				self.id_client = datajson.get("id")
				self.cnpj = datajson.get("cpfCnpj")

				#criar nota
				


				url = f"{ASAAS_BASE_URL}/invoices"

				payload = json.dumps({
						"customer": self.id_client,
						"installment": None,
						"serviceDescription": _format_description(self.descricao_do_servico),
						"observations": self.observacoes_adicionais,
						"value": self.net_total,
						"deductions": self.deducoes,
						"effectiveDate": self.data_emissao,
						"externalReference": None,
						"taxes": {
							"retainIss": retencao_imposto,
							"iss": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "aliquota"),
							"cofins": self.cofins,
							"csll": self.csll,
							"inss": self.inss,
							"ir": self.irrf,
							"pis": self.pis,
							"nbsCode": _extract_code(self.nbs_code),
							"taxSituationCode": _extract_code(self.tax_situation_code),
							"taxClassificationCode": _extract_code(self.tax_classification_code),
							"operationIndicatorCode": _extract_code(self.operation_indicator_code),
							"pisCofinsRetentionType": retention_type_map.get(self.pis_cofins_retention_type) or None,
							**( {"pisCofinsTaxStatus": tax_status_map.get(_extract_code(self.pis_cofins_tax_status))}
								if self.pis_cofins_tax_status
								else {} )
						},
						"municipalServiceId": None,
						"municipalServiceCode": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "service_code"),
						"municipalServiceName": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "descricao")
						})
				headers = {
						'Content-Type': 'application/json',
						'access_token': ASAAS_TOKEN,
						'Cookie': 'AWSALB=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBCORS=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBTG=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; AWSALBTGCORS=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; JSESSIONID=4442277196883DA883F1E02313B2C440ABB9C1245A1699B51350BDAA4AA6F4FB2D88CA765F4B3CCAC5D8838D4612D270E9A7836E02F312EFEE7BF9AA1EEF3394.n2'
						}

				response = requests.request("POST", url, headers=headers, data=payload)
				datajson = json.loads(response.text)
				if not datajson.get("id"):
					frappe.log_error(title="Asaas Invoice Error", message=response.text)
					frappe.throw(f"Erro ao criar nota no Asaas: {response.text}")
				self.id_nfs = datajson.get("id")
				self.name = self.id_nfs
				totalcofins = self.net_total * float(self.cofins) / 100
				self.totalcofins = totalcofins 
				totalirrf = self.net_total * float(self.irrf) / 100
				self.totalirrf = totalirrf
				totalpis = self.net_total * float(self.pis) / 100
				self.totalpis = totalpis
				totalcsll = self.net_total * float(self.csll) / 100
				self.totalcsll = totalcsll
				totalinss = self.net_total * float(self.inss) / 100
				self.totalinss = totalinss
				#totaldeducoes = self.base_total - float(self.deducoes)
				#self.totaldeducoes = totaldeducoes
				self.totalliquidoboleto = self.net_total - (totalcofins + totalirrf + totalpis + totalcsll + totalinss) 
				self.totalliquidoboleto = self.totalliquidoboleto - float(self.deducoes)

			else:

				#cliente existe apenas criar nota


				url = f"{ASAAS_BASE_URL}/customers?cpfCnpj="+str(frappe.db.get_value("Customer", self.customer, "cnpj"))
				headers = {
				'Content-Type': 'application/json',
				'access_token': ASAAS_TOKEN,
				'Cookie': 'AWSALB=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBCORS=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBTG=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; AWSALBTGCORS=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
				}

				response = requests.request("GET", url, headers=headers, data=payload)
				
				print(response.text)
				datajson = json.loads(response.text)
				if not datajson.get('data'):
					frappe.throw(f"Erro ao buscar cliente no Asaas: {response.text}")
				info_customer = datajson['data'][0]
				self.id_client = info_customer['id']

				#criar nota
			
				
				url = f"{ASAAS_BASE_URL}/invoices"

				payload = json.dumps({
						"customer": self.id_client,
						"installment": None,
						"serviceDescription": _format_description(self.descricao_do_servico),
						"observations": self.observacoes_adicionais,
						"value": self.net_total,
						"deductions": self.deducoes,
						"effectiveDate": self.data_emissao,
						"externalReference": None,
						"taxes": {
							"retainIss": retencao_imposto,
							"iss": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "aliquota"),
							"cofins": self.cofins,
							"csll": self.csll,
							"inss": self.inss,
							"ir": self.irrf,
							"pis": self.pis,
							"nbsCode": _extract_code(self.nbs_code),
							"taxSituationCode": _extract_code(self.tax_situation_code),
							"taxClassificationCode": _extract_code(self.tax_classification_code),
							"operationIndicatorCode": _extract_code(self.operation_indicator_code),
							"pisCofinsRetentionType": retention_type_map.get(self.pis_cofins_retention_type) or None,
							**( {"pisCofinsTaxStatus": tax_status_map.get(_extract_code(self.pis_cofins_tax_status))}
								if self.pis_cofins_tax_status
								else {} )
						},
						"municipalServiceId": None,
						"municipalServiceCode": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "service_code"),
						"municipalServiceName": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "descricao")
						})
				headers = {
						'Content-Type': 'application/json',
						'access_token': ASAAS_TOKEN,
						'Cookie': 'AWSALB=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBCORS=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBTG=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; AWSALBTGCORS=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; JSESSIONID=4442277196883DA883F1E02313B2C440ABB9C1245A1699B51350BDAA4AA6F4FB2D88CA765F4B3CCAC5D8838D4612D270E9A7836E02F312EFEE7BF9AA1EEF3394.n2'
						}

				response = requests.request("POST", url, headers=headers, data=payload)
				datajson = json.loads(response.text)
				if not datajson.get("id"):
					frappe.log_error(title="Asaas Invoice Error", message=response.text)
					frappe.throw(f"Erro ao criar nota no Asaas: {response.text}")
				self.id_nfs = datajson.get("id")
				self.name = self.id_nfs
				totalcofins = self.net_total * float(self.cofins) / 100
				self.totalcofins = totalcofins 
				totalirrf = self.net_total * float(self.irrf) / 100
				self.totalirrf = totalirrf
				totalpis = self.net_total * float(self.pis) / 100
				self.totalpis = totalpis
				totalcsll = self.net_total * float(self.csll) / 100
				self.totalcsll = totalcsll
				totalinss = self.net_total * float(self.inss) / 100
				self.totalinss = totalinss
				#totaldeducoes = self.base_total - float(self.deducoes)
				#self.totaldeducoes = totaldeducoes
				self.totalliquidoboleto = self.net_total - (totalcofins + totalirrf + totalpis + totalcsll + totalinss) 
				self.totalliquidoboleto = self.totalliquidoboleto - float(self.deducoes)

		elif self.situacao_nota == "Cancelada":
			def time_now():
				now = datetime.now(timezone("America/Sao_Paulo")).strftime(
					"%d/%m/%Y"
				)
				return now
			url = f"{ASAAS_BASE_URL}/invoices/"+self.name+"/cancel"

			payload={}
			headers = {
			'Content-Type': 'application/json',
			'access_token': ASAAS_TOKEN,
			'Cookie': 'AWSALB=HnwITygiNzfhoD5piNj2Vwu4QfKrMNkw2yhCa1vtd2ChtHBhutdyw9jIN1AK4Fqu0VUbwc5A7n55jYDXYX071c3qGFFhF3YhBbsxUH/zqt5IuiXop+QjsQ0R0dOy; AWSALBCORS=HnwITygiNzfhoD5piNj2Vwu4QfKrMNkw2yhCa1vtd2ChtHBhutdyw9jIN1AK4Fqu0VUbwc5A7n55jYDXYX071c3qGFFhF3YhBbsxUH/zqt5IuiXop+QjsQ0R0dOy; AWSALBTG=27+foNdPtL5Qm/IF/j/MXXG0oRPRBAqd7JKfYmJ5+vUjpMmCtGEADgC99Mi8bRNe/7772YoVivDsfYgfPe3l3YfkCT6A2eEygcC7CPAKstHo4g5bcuUoUucktoUhBCPnEHhrRRRpm4xX+6F1atOgNZHK2ne+48WXsyrkqwHznTzr; AWSALBTGCORS=27+foNdPtL5Qm/IF/j/MXXG0oRPRBAqd7JKfYmJ5+vUjpMmCtGEADgC99Mi8bRNe/7772YoVivDsfYgfPe3l3YfkCT6A2eEygcC7CPAKstHo4g5bcuUoUucktoUhBCPnEHhrRRRpm4xX+6F1atOgNZHK2ne+48WXsyrkqwHznTzr'
			}

			response = requests.request("POST", url, headers=headers, data=payload)
			

			print(response.text)
			self.data_cancelamento = time_now()
			
	

	#emitir nota
	def on_submit(self):
		url2 = f"{ASAAS_BASE_URL}/invoices/{self.name}/authorize"
		headers = {
			'Content-Type': 'application/json',
			'access_token': ASAAS_TOKEN,
		}
		response2 = requests.request("POST", url2, headers=headers)
		datajson2 = json.loads(response2.text)

		if datajson2.get("errors"):
			frappe.log_error(title="Asaas Authorize Error", message=response2.text)
			frappe.throw(f"Erro ao autorizar nota no Asaas: {response2.text}")

		self.db_set("numero_nfs", datajson2.get("number"))
		self.db_set("pdf_nota", datajson2.get("pdfUrl"))
		self.db_set("xml_nota", datajson2.get("xmlUrl"))
		self.db_set("status", datajson2.get("status"))


@frappe.whitelist()
def atualizar_status_nota(docname):
	doc = frappe.get_doc("NFS", docname)
	url = f"{ASAAS_BASE_URL}/invoices/{doc.id_nfs}"
	headers = {
		'Content-Type': 'application/json',
		'access_token': ASAAS_TOKEN,
	}
	response = requests.request("GET", url, headers=headers)
	datajson = json.loads(response.text)

	if datajson.get("errors"):
		frappe.log_error(title="Asaas Status Error", message=response.text)
		frappe.throw(f"Erro ao buscar nota no Asaas: {response.text}")

	doc.db_set("numero_nfs", datajson.get("number"))
	doc.db_set("pdf_nota", datajson.get("pdfUrl"))
	doc.db_set("xml_nota", datajson.get("xmlUrl"))
	doc.db_set("status", datajson.get("status"))

	return datajson.get("status")
			


	


			


		


	





		



