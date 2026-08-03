# Copyright (c) 2026, laugusto and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

import re

from ordem_servico.doc_events.codigo_padrao import CODIGO_INSTRUMENTO_RE


class PadraodeCalibracao(Document):
	def validate(self):
		self._validar_codigo()
		self._validar_datas()

	def _validar_codigo(self):
		"""O código é livre de formato: novas famílias de padrão surgem com o
		tempo (MR3, MRC1, 26605.01...). Só recusamos o que claramente não é um
		código; a família de instrumentos é normalizada para o código base."""
		codigo = (self.codigo or "").strip()

		if not codigo:
			frappe.throw("Informe o <b>Código do Padrão</b>.")

		if re.search(r"\d{2}[-/]\d{2}[-/]\d{4}", codigo):
			frappe.throw(
				"O código não pode conter uma data: <b>{}</b>.<br>"
				"Informe apenas o código do padrão (ex: H001A03FD, 26605.01, MRC1).".format(codigo)
			)

		# Instrumentos: normaliza removendo sufixo de canal ('- T' / '- H')
		instrumento = CODIGO_INSTRUMENTO_RE.search(codigo.upper())
		if instrumento and codigo.upper().startswith(instrumento.group(0)):
			self.codigo = instrumento.group(0)
		else:
			self.codigo = codigo

	def _validar_datas(self):
		# Validade é obrigatória: é ela, junto do código, que casa o padrão com a OS.
		if not self.validade:
			frappe.throw("Preencha a <b>Validade da Calibração</b>.")


@frappe.whitelist()
def padroes_vencendo(dias=60):
	"""Padrões vencidos ou a vencer nos próximos N dias.

	Usar padrão vencido invalida a rastreabilidade da calibração, então vale
	acompanhar de perto. Considera apenas a versão mais recente de cada código.
	"""
	from frappe.utils import add_days, getdate, nowdate

	limite = add_days(nowdate(), int(dias))
	hoje = getdate(nowdate())

	registros = frappe.get_all(
		"Padrao de Calibracao",
		filters={"validade": ["<=", limite]},
		fields=["name", "codigo", "descricao", "validade"],
		order_by="validade asc",
	)

	# Um código pode ter várias versões; só interessa a de maior validade
	mais_recente = {}
	for r in registros:
		atual = mais_recente.get(r.codigo)
		if not atual or getdate(r.validade) > getdate(atual.validade):
			mais_recente[r.codigo] = r

	# Descarta os que já foram recalibrados (existe versão mais nova válida)
	vigentes = frappe.get_all(
		"Padrao de Calibracao",
		filters={"validade": [">", limite]},
		pluck="codigo",
	)
	vigentes = set(vigentes)

	resultado = []
	for codigo, r in mais_recente.items():
		if codigo in vigentes:
			continue
		validade = getdate(r.validade)
		resultado.append({
			"name": r.name,
			"codigo": codigo,
			"descricao": r.descricao,
			"validade": str(validade),
			"dias": (validade - hoje).days,
			"situacao": "Vencido" if validade < hoje else "A vencer",
		})

	resultado.sort(key=lambda x: x["dias"])
	return resultado
