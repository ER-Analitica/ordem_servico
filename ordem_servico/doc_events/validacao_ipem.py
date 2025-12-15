from __future__ import unicode_literals
import frappe
import re

def validacao_ipem(self, method):

    nome = (self.equipment_description or "").lower()

    # Regex mais forte para variações de "balança"
    regex_balanca = re.compile(r"\bb+a+l+a*n*[çc]a+\b")

    eh_balanca = bool(regex_balanca.search(nome))

    if not eh_balanca:
        return

    if self.manutencao_preventiva or self.manutencao_corretiva:

        campos_faltantes = []

        if not self.lacre_retirado:
            campos_faltantes.append("Lacre Retirado")

        if not self.lacre_afixado:
            campos_faltantes.append("Lacre Afixado")

        if not self.observacoes_ipem:
            campos_faltantes.append("Observações IPEM")

        if campos_faltantes:
            mensagem = (
                "Para prosseguir, preencha os seguintes campos obrigatórios relacionados ao IPEM:<br><br>"
                + "<br>".join(f"- {c}" for c in campos_faltantes)
            )
            frappe.throw(mensagem)
