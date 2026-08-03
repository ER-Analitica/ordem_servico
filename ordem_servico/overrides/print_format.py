"""Nome amigável também no download do PDF.

O envio por e-mail e o download usam caminhos diferentes no Frappe: o e-mail
passa por `Communication.mail_attachments`, o download por
`frappe.utils.print_format.download_pdf`. Aqui cobrimos o segundo, para que o
arquivo baixado tenha o mesmo nome do que é enviado ao cliente.

A regra de nomeação é a mesma (mapa NOMES_AMIGAVEIS): apenas os pares
doctype + formato de impressão previstos são renomeados; o resto do sistema
mantém o comportamento padrão.
"""

import frappe

from ordem_servico.overrides.communication import montar_nome_do_anexo


@frappe.whitelist(allow_guest=True)
def download_pdf(
    doctype: str,
    name: str,
    format=None,
    doc=None,
    no_letterhead=0,
    language=None,
    letterhead=None,
    pdf_generator=None,
):
    from frappe.utils.print_format import download_pdf as _download_pdf_original

    _download_pdf_original(
        doctype,
        name,
        format=format,
        doc=doc,
        no_letterhead=no_letterhead,
        language=language,
        letterhead=letterhead,
        pdf_generator=pdf_generator,
    )

    try:
        amigavel = montar_nome_do_anexo(doctype, name, format)
    except Exception:
        amigavel = None

    if amigavel:
        frappe.local.response.filename = "{}.pdf".format(amigavel)
