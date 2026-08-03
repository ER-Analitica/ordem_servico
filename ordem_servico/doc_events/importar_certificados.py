import frappe

DOCTYPES_PERMITIDOS = ("Ordem Servico Interna", "Ordem Servico Externa")


@frappe.whitelist()
def anexar_certificado_forcado(doctype, name, file_url):
    """Anexa um certificado à OS (Interna ou Externa) sem rodar o validate().

    Usado pela importação em lote de certificados legados, cujas OS antigas
    não têm os dados obrigatórios (data de calibração, equipamento) exigidos
    pelas validações criadas posteriormente.
    """
    if doctype not in DOCTYPES_PERMITIDOS:
        frappe.throw("DocType inválido para anexo de certificado.")

    if not frappe.has_permission(doctype, "write", name):
        frappe.throw("Sem permissão para atualizar esta Ordem de Serviço.")

    valor_atual = frappe.db.get_value(doctype, name, "anexo_certificado")
    ja_anexado = bool(valor_atual and file_url in valor_atual)

    if ja_anexado:
        novo_valor = valor_atual
    else:
        novo_valor = f"{valor_atual}\n{file_url}" if valor_atual else file_url
        frappe.db.set_value(
            doctype,
            name,
            "anexo_certificado",
            novo_valor,
            update_modified=False,
        )
        # O set_value acima não invalida o cache do documento; sem isso a
        # extração leria o anexo_certificado antigo.
        frappe.clear_document_cache(doctype, name)

    # Extrai a rastreabilidade dos padrões. Roda quando o anexo é novo ou
    # quando a OS ainda não tem a tabela preenchida (permite reprocessar
    # certificados anexados antes desta funcionalidade existir).
    rastreabilidade = None
    tem_rastreabilidade = frappe.db.exists(
        "Rastreabilidade Padrao OS",
        {"parent": name, "parenttype": doctype, "parentfield": "rastreabilidade_padroes"},
    )
    if not ja_anexado or not tem_rastreabilidade:
        # Nunca deve quebrar o anexo — em caso de erro, apenas registra no log.
        try:
            from ordem_servico.doc_events.rastreabilidade_padroes import extrair_rastreabilidade

            rastreabilidade = extrair_rastreabilidade(doctype, name)
        except Exception:
            frappe.log_error(
                title="Falha na extração de rastreabilidade de padrões",
                message=frappe.get_traceback(),
            )

    return {"ja_anexado": ja_anexado, "valor": novo_valor, "rastreabilidade": rastreabilidade}
