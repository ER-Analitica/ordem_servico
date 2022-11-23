# -*- coding: utf-8 -*-
# Copyright (c) 2022, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json

from frappe.model.document import Document

#Criar nfs

class NFS(Document):
	def before_save(self):
		global retencao_imposto
		if self.imposto_retido == "NÃO":
			retencao_imposto = False
			
		else:
			retencao_imposto = True
		#listar cliente
		url = "https://sandbox.asaas.com/api/v3/customers?cpfCnpj="+str(frappe.db.get_value("Customer", self.customer, "cnpj"))
		payload={}
		headers = {
		'Content-Type': 'application/json',
		'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDExNDQ6OiRhYWNoX2QzYWZiZmI3LWYwZTAtNGU4Yi05MGQ5LTBiZTM4ODBhNzA4MA==',
		'Cookie': 'AWSALB=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBCORS=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBTG=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; AWSALBTGCORS=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
		}

		response = requests.request("GET", url, headers=headers, data=payload)
		
		print(response.text)
		datajson = json.loads(response.text)
		self.client_exist = datajson.get("totalCount")	

		#Cliente não existe
		if self.client_exist == 0:
		
			#criar cliente 
			url = "https://sandbox.asaas.com/api/v3/customers"

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
						'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDExNDQ6OiRhYWNoX2QzYWZiZmI3LWYwZTAtNGU4Yi05MGQ5LTBiZTM4ODBhNzA4MA==',
						'Cookie': 'AWSALB=NDsZE6HSGykB5Q/ryMenP5mW4vs3e+cc2Ed+0RscpplUQ/9TphPnQhYnPH5iTM59Ddtpm9FrWGyy+q4cikvIQw2eggvGHPUAB2Q47Iz7FzPK1LpaCMFmK1FbDYLu; AWSALBCORS=NDsZE6HSGykB5Q/ryMenP5mW4vs3e+cc2Ed+0RscpplUQ/9TphPnQhYnPH5iTM59Ddtpm9FrWGyy+q4cikvIQw2eggvGHPUAB2Q47Iz7FzPK1LpaCMFmK1FbDYLu; AWSALBTG=cuofeg0H83YZQFE3ZHLeoAlPHCxQbHHVpYfQWxHhrWZuWPbj5nhcbjhbziMSqKF7zqkPW+pg3HhCJQInzc5KFkGip1Fr+gXZ/1Ql1PSdeG31RpnqjZSrjvMCxtCh8kSi/VQof4lxksWUlJ9YdvgVn+DY5qLXIMsCLJ4sPHzFyTfJ; AWSALBTGCORS=cuofeg0H83YZQFE3ZHLeoAlPHCxQbHHVpYfQWxHhrWZuWPbj5nhcbjhbziMSqKF7zqkPW+pg3HhCJQInzc5KFkGip1Fr+gXZ/1Ql1PSdeG31RpnqjZSrjvMCxtCh8kSi/VQof4lxksWUlJ9YdvgVn+DY5qLXIMsCLJ4sPHzFyTfJ; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
						}

			response = requests.request("POST", url, headers=headers, data=payload)

			print(response.text)
			datajson = json.loads(response.text)
			self.id_client = datajson.get("id")
			self.cnpj = datajson.get("cpfCnpj")

			#criar nota
			
			global id
			url = "https://sandbox.asaas.com/api/v3/invoices"

			payload = json.dumps({
					"customer": self.id_client,
					"installment": None,
					"serviceDescription": self.descricao_servico,
					"observations": self.observacoes_adicionais,
					"value": self.base_total,
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
						"pis": self.pis
					},
					"municipalServiceId": None,
					"municipalServiceCode": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "service_code"),
					"municipalServiceName": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "descricao")
					})
			headers = {
					'Content-Type': 'application/json',
					'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDExNDQ6OiRhYWNoX2QzYWZiZmI3LWYwZTAtNGU4Yi05MGQ5LTBiZTM4ODBhNzA4MA==',
					'Cookie': 'AWSALB=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBCORS=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBTG=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; AWSALBTGCORS=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; JSESSIONID=4442277196883DA883F1E02313B2C440ABB9C1245A1699B51350BDAA4AA6F4FB2D88CA765F4B3CCAC5D8838D4612D270E9A7836E02F312EFEE7BF9AA1EEF3394.n2'
					}

			response = requests.request("POST", url, headers=headers, data=payload)

			print(response.text)
			datajson = json.loads(response.text)
			self.id_nfs = datajson.get("id")
			id = self.id_nfs
			self.name = id


		else:

			#cliente existe apenas criar nota


			url = "https://sandbox.asaas.com/api/v3/customers?cpfCnpj="+str(frappe.db.get_value("Customer", self.customer, "cnpj"))
			headers = {
			'Content-Type': 'application/json',
			'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDExNDQ6OiRhYWNoX2QzYWZiZmI3LWYwZTAtNGU4Yi05MGQ5LTBiZTM4ODBhNzA4MA==',
			'Cookie': 'AWSALB=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBCORS=ItIk5WPDi/zCe99PKb7U3/JALkwcWUTDRS6y58f5vI9NQYp6JgMmvmBvLXmZ+zrCQpCWYCPArXawoUFiQEpuOkQZgovQq1mq6eeArzTzBLjn+1TT1yk9A4mkaJ6i; AWSALBTG=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; AWSALBTGCORS=CQ41WfveC9deQP0Biq0vaPilPfOhsn+yCt5X8YsqztdFm2TlPMa/9GkfXsP5PmKWxB7UYXZoBME3y9aPcTiJUTI3SbSYMRbdOEioO9lr5CXDq50w028jEvRYGt/axwp0VJ8Bz4dWE1RmFHYGVNDvJzeIn9deKqvLryoWxGpc2Nf/; JSESSIONID=8728B03FD2C0905324D8BB3AC2EBA48BA60307F616A5655CB8DCD23281D6FA3FCB1873C3D15F5B0DB19FFA284A4538196265212522502A348940AEC0BEB10BC2.n2'
			}

			response = requests.request("GET", url, headers=headers, data=payload)
			
			print(response.text)
			datajson = json.loads(response.text)	
			info_customer = datajson['data'][0]
			self.id_client = info_customer['id']

			#criar nota
		
			global id
			url = "https://sandbox.asaas.com/api/v3/invoices"

			payload = json.dumps({
					"customer": self.id_client,
					"installment": None,
					"serviceDescription": self.descricao_servico,
					"observations": self.observacoes_adicionais,
					"value": self.base_total,
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
						"pis": self.pis
					},
					"municipalServiceId": None,
					"municipalServiceCode": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "service_code"),
					"municipalServiceName": frappe.db.get_value("Codigo de Servico", self.cod_do_servico, "descricao")
					})
			headers = {
					'Content-Type': 'application/json',
					'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDExNDQ6OiRhYWNoX2QzYWZiZmI3LWYwZTAtNGU4Yi05MGQ5LTBiZTM4ODBhNzA4MA==',
					'Cookie': 'AWSALB=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBCORS=ZTvGz3bitbdssS5kbR9L9hnJmJRU8prMDfgI9VqS+BwaN5FalxQccWRm9ZxCwkTUmn52oym3t12T2rBP9k312j2JTLy82C+UeMxt9uBrtNBU4Kc09z4ujJBKf/4F; AWSALBTG=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; AWSALBTGCORS=IXQlYcAFDgfgubk867yJuzaKs+Yss+X8zoqNNsVv+csMfq0DCs2tmK36+l2euLge/APhUC+67hq3REOcIgTUnjhJuZE3kgl0ixrUyBciSK1Ina5ZQMb3pP4o+hxvGUDyPBX58M28vDJ8ozbrktD4P5cs5vk0a8EkOuWaFmufy4nc; JSESSIONID=4442277196883DA883F1E02313B2C440ABB9C1245A1699B51350BDAA4AA6F4FB2D88CA765F4B3CCAC5D8838D4612D270E9A7836E02F312EFEE7BF9AA1EEF3394.n2'
					}

			response = requests.request("POST", url, headers=headers, data=payload)

			print(response.text)
			datajson = json.loads(response.text)
			self.id_nfs = datajson.get("id")
			id = self.id_nfs
			self.name = id


	#emitir nota
	def on_submit(self):
		#self.company = id
			url2 = "https://sandbox.asaas.com/api/v3/invoices/"+str(self.name)+"/authorize"
			headers = {
			'Content-Type': 'application/json',
			'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAwNDExNDQ6OiRhYWNoX2QzYWZiZmI3LWYwZTAtNGU4Yi05MGQ5LTBiZTM4ODBhNzA4MA==',
			'Cookie': 'AWSALB=p2L20Wh0ST77WVsEInwqzthi8HXxg2UjnZk/8krfbbg37WHbr/4aMTrkaS6urZvFoTezL5L2XF4gms3Nv2zJs5Y0cfuHylz2hZ20Mp3sTpZOAlmIc6vGEMa+q57F; AWSALBCORS=p2L20Wh0ST77WVsEInwqzthi8HXxg2UjnZk/8krfbbg37WHbr/4aMTrkaS6urZvFoTezL5L2XF4gms3Nv2zJs5Y0cfuHylz2hZ20Mp3sTpZOAlmIc6vGEMa+q57F; AWSALBTG=+oSgKZ8vwWtJ2bXQG7BKeI4SxmEObBDoyT3cURMndwJvJVhcn7cYP5y9LvE0PnT9U2YbfmAwj4CODqRk33poY9VkzIWlTMegXBujNXN8P93pX+Qur4HJu/RNuc2nK9uxXoPJJAz34m2CczWWFE+Hw+yUm+Vx3vlJm8xhZV9U7Pn9; AWSALBTGCORS=+oSgKZ8vwWtJ2bXQG7BKeI4SxmEObBDoyT3cURMndwJvJVhcn7cYP5y9LvE0PnT9U2YbfmAwj4CODqRk33poY9VkzIWlTMegXBujNXN8P93pX+Qur4HJu/RNuc2nK9uxXoPJJAz34m2CczWWFE+Hw+yUm+Vx3vlJm8xhZV9U7Pn9'
			}
			response2 = requests.request("POST", url2, headers=headers)



		


	





		



