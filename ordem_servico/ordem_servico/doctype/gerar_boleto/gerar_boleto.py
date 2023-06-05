# -*- coding: utf-8 -*-
# Copyright (c) 2022, laugusto and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
import requests
import json

from frappe.model.document import Document


class GerarBoleto(Document):
	def before_save(self):
			tipo_desconto = ""
			campo_desconto = ""
			tipo_multa = ""
			campo_multa = ""
			tipo_pagamento = ""
			
			if self.forma_de_pagamento == "Boleto Bancário":
				tipo_pagamento = "BOLETO"
			elif self.forma_de_pagamento == "Cartão de Crédito":
				tipo_pagamento = "CREDIT_CARD"
			elif self.forma_de_pagamento == "Pix":
				tipo_pagamento = "PIX"
			elif self.forma_de_pagamento == "Perguntar ao Cliente":
				tipo_pagamento = "UNDEFINED"

			if self.desconto == "Valor percentual":
				tipo_desconto = "PERCENTAGE"
				campo_desconto = self.percentual_desconto
			elif self.desconto == "Valor fixo":
				tipo_desconto = "FIXED"
				campo_desconto = self.valor_fixo_desconto

			if self.multa_atraso == "Valor percentual":
				tipo_multa = "PERCENTAGE"
				campo_multa = self.percentual_multa
			elif self.multa_atraso == "Valor fixo":
				tipo_multa = "FIXED"
				campo_multa = self.fixo_multa


			url3 = "https://asaas.com/api/v3/payments"
			payload = json.dumps({
			"customer": self.id_client,
			"billingType": tipo_pagamento,
			"dueDate": self.data_vencimento_cobranca,
			"totalValue": self.totalliquidoboleto,
			"installmentCount":self.parcelas,
			"description": self.cobranca_description,
			"discount": {
				"value": campo_desconto,
				"dueDateLimitDays": self.dias_antes_vencimento,
				"type": tipo_desconto
			},
			"fine": {
				"value": campo_multa,
				"type": tipo_multa
			},
			"interest": {
				"value": self.juros_mes,
			}
			})
			headers = {
			'Content-Type': 'application/json',
			'access_token': '$aact_YTU5YTE0M2M2N2I4MTliNzk0YTI5N2U5MzdjNWZmNDQ6OjAwMDAwMDAwMDAwMDAyNjA5NzM6OiRhYWNoXzQ0YWMzZDRmLTE4NDEtNDY3Ny04NGFkLTQ0NzVjMDEwYTk4Mg==',
			'Cookie': 'AWSALB=F6M2jKnZcC1dnXNvg2Bc+fm0i/5HEYpuJnyrR9Gn2sPURTgwIj11tdZ3KIwF2PoOdVY4z8YuYbTFpGrxO+7yh+jI2TeSR+fFiP8AXD3PaW+RFfypxKtf1c0Os51T; AWSALBCORS=F6M2jKnZcC1dnXNvg2Bc+fm0i/5HEYpuJnyrR9Gn2sPURTgwIj11tdZ3KIwF2PoOdVY4z8YuYbTFpGrxO+7yh+jI2TeSR+fFiP8AXD3PaW+RFfypxKtf1c0Os51T; AWSALBTG=CxiaQYlOObhdnPMx1VghlMEvse6OmCAzOW5D2ZTaJ9grnTPmK6+IJg89tygPl4HX5KBCyeiNoapwGuq2SFGinVRqrAQqt/xg44b3vaDZ2QhgsKSZspFWRzZmlD3YdI+GX680M4WVIhA8MW05OILDfLvd96mwrmsBRGjSTTrij+tv; AWSALBTGCORS=CxiaQYlOObhdnPMx1VghlMEvse6OmCAzOW5D2ZTaJ9grnTPmK6+IJg89tygPl4HX5KBCyeiNoapwGuq2SFGinVRqrAQqt/xg44b3vaDZ2QhgsKSZspFWRzZmlD3YdI+GX680M4WVIhA8MW05OILDfLvd96mwrmsBRGjSTTrij+tv'
			}

			response = requests.request("POST", url3, headers=headers, data=payload)

			print(response.text)
			datajson = json.loads(response.text)
			self.id_parcela = datajson.get("installment")
			self.link_cobranca = datajson.get("invoiceUrl")
			self.status_cobranca = datajson.get("status")

	
			


			

			


		


	





		



