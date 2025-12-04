from __future__ import unicode_literals
import frappe

def validacao_ipem(self, method):
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
