import frappe


@frappe.whitelist()
def anexar_certificado_forcado(name, file_url):
    """Anexa um certificado à OS Externa sem rodar o validate() do documento.

    Usado pela importação em lote de certificados legados, cujas OS antigas
    não têm os dados obrigatórios (data de calibração, equipamento) exigidos
    pelas validações criadas posteriormente.
    """
    if not frappe.has_permission("Ordem Servico Externa", "write", name):
        frappe.throw("Sem permissão para atualizar esta Ordem de Serviço.")

    valor_atual = frappe.db.get_value("Ordem Servico Externa", name, "anexo_certificado")

    if valor_atual and file_url in valor_atual:
        return {"ja_anexado": True, "valor": valor_atual}

    novo_valor = f"{valor_atual}\n{file_url}" if valor_atual else file_url

    frappe.db.set_value(
        "Ordem Servico Externa",
        name,
        "anexo_certificado",
        novo_valor,
        update_modified=False,
    )

    return {"ja_anexado": False, "valor": novo_valor}
