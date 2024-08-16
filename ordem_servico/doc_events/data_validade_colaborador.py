from __future__ import unicode_literals
import frappe

from datetime import datetime, timedelta

#somando dias em uma data dentro de documentos internos no colaborador
def validate(self, method):
    try:
        for documento_interno in self.documentos_internos:
            # Verifica se 'emissao' é uma string e converte para um objeto datetime
            if isinstance(documento_interno.emissao, str):
                documento_interno.emissao = datetime.strptime(documento_interno.emissao, '%Y-%m-%d').date()

            validade = int(documento_interno.validade)
            
            # Adiciona o número de dias de 'validade' à data 'emissao'
            documento_interno.data_validade = documento_interno.emissao + timedelta(days=validade)
    except:
        frappe.throw("Erro: Não é possível adicionar uma linha ao documento sem preencher os campos 'Emissão' e 'Validade'")
