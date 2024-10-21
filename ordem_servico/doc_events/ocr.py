#aplicável para ler imagens e armazenar informações
import easyocr

import frappe

from frappe.utils.file_manager import get_file_path

@frappe.whitelist()
def process_image(doc, method):
    # Cria um leitor OCR para o idioma desejado
    reader = easyocr.Reader(['pt'])  # Ajuste o idioma conforme necessário

    # Obtenha o caminho do arquivo de imagem
    file_path = get_file_path(doc.ocr)
    
    # Leia o texto da imagem
    result = reader.readtext(file_path)

    # Concatena o texto extraído
    extracted_text = " ".join([text for _, text, _ in result])

    # Armazene o texto extraído no campo 'texto'
    doc.texto_ocr = extracted_text
    #doc.primeira_linha = doc.texto.split(" ")[12]
    #doc.campo1 = doc.texto.split(" ")[22]
    #doc.campo2 = doc.texto.split(" ")[33]

# Vincule o método ao evento on_update
#frappe.db.add_custom_script('EasyOCR', 'validate', 'process_image')

