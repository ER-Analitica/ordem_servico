#muito aplicável para casos de conversões de word para pdf como exemplo
import PyPDF2

import frappe

from frappe.utils.file_manager import get_file_path

@frappe.whitelist()
def process_pdf(doc, method):
  

    # Obtenha o caminho do arquivo de imagem
    file_path = get_file_path(doc.pdf)

    with open(file_path,"rb") as arquivo:
        leitor_pdf = PyPDF2.PdfReader(arquivo)
        texto = ""
        for pagina in leitor_pdf.pages:
            texto += pagina.extract_text()

    doc.texto_pdf = texto