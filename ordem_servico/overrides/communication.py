"""Nome amigável para o PDF anexado nos e-mails enviados pelo desk.

Por padrão o Frappe nomeia o anexo com o ID do documento (ex: "oep6mi4t1q.pdf"),
o que não diz nada para o cliente. Aqui trocamos por um nome legível.

O Frappe remove espaços do nome do arquivo (frappe.attach_print), então os
nomes são montados já com "_" no lugar de espaço.
"""

import re

import frappe
from frappe.core.doctype.communication.communication import Communication

# (doctype, formato de impressão) -> (rótulo do arquivo, campo do cliente)
# Só os pares listados aqui ganham nome amigável; qualquer outro formato ou
# doctype mantém o comportamento padrão do Frappe (ID do documento).
NOMES_AMIGAVEIS = {
    ("Criador de Ordens de Servico em Lote", "Relatorio de Servico"): (
        "Relatório de Serviço",
        "cliente",
    ),
}


# O frappe.attach_print remove espaços comuns do nome do arquivo. Para o anexo
# do e-mail usamos o espaço não separável, que sobrevive e é exibido como um
# espaço normal. No download não há essa limitação e usamos o espaço comum.
ESPACO_PRESERVADO = " "


def _limpar(texto, espaco=" "):
    """Tira caracteres inválidos em nome de arquivo e normaliza os espaços."""
    texto = re.sub(r"[\\/:*?\"<>|]", "", texto or "").strip()
    return re.sub(r"\s+", espaco, texto)


def _nome_do_cliente(doctype, name, campo):
    cliente = frappe.db.get_value(doctype, name, campo)
    if not cliente:
        return ""
    # O Link guarda o ID (ex: CLIENTE-01216); busca o nome de exibição
    return frappe.db.get_value("Customer", cliente, "customer_name") or cliente


def montar_nome_do_anexo(doctype, name, print_format=None, espaco=" "):
    """Nome amigável do PDF, ou None para manter o padrão do Frappe."""
    config = NOMES_AMIGAVEIS.get((doctype, print_format))
    if not config:
        return None

    rotulo, campo_cliente = config
    partes = [rotulo]

    cliente = _nome_do_cliente(doctype, name, campo_cliente)
    if cliente:
        partes.append(cliente)

    return _limpar(" - ".join(partes), espaco=espaco)


class OrdemServicoCommunication(Communication):
    def mail_attachments(self, print_format=None, print_html=None, print_language=None):
        anexos = super().mail_attachments(
            print_format=print_format,
            print_html=print_html,
            print_language=print_language,
        )

        for anexo in anexos:
            if not isinstance(anexo, dict) or anexo.get("print_format_attachment") != 1:
                continue
            try:
                amigavel = montar_nome_do_anexo(
                    anexo.get("doctype"),
                    anexo.get("name"),
                    anexo.get("print_format"),
                    espaco=ESPACO_PRESERVADO,
                )
            except Exception:
                amigavel = None
            if amigavel:
                anexo["file_name"] = amigavel

        return anexos
