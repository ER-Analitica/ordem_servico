from __future__ import unicode_literals
import frappe

def analise_critica_campos_vazios(self, method):
    # Lista para armazenar os nomes dos campos que estão vazios
    campos_vazios = []

    # Verifica os campos obrigatórios e adiciona à lista se estiverem vazios
    if not self.tipo_de_faturamento:
        campos_vazios.append("Tipo de Faturamento")
    if not self.faturamento_parcial:
        campos_vazios.append("Faturamento Parcial")
    if not self.confirmacao_do_cliente:
        campos_vazios.append("Confirmação do Cliente")
    
    # Se houver campos vazios, gerar um aviso
    if campos_vazios:
        campos_str = ", ".join(campos_vazios)
        mensagem = (
            f"{frappe.session.user}, não será possível enviar este pedido ainda, "
            f"pois os campos {campos_str} estão vazios. Por gentileza, verifique."
        )
        frappe.throw(mensagem)
